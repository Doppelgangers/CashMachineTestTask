import io
from datetime import datetime


from django.http.response import FileResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from cash_machine.utils import get_items_by_ids, convert_list_items_for_count_dict, create_check, create_qr_for_url
from fictionalstore import settings
from fictionalstore.serializers import ItemsListSerializer


# Create your views here.

class CashMachineApi(APIView):
    def post(self, request):
        # Сериализация и проверка входящих данных
        serializer = ItemsListSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        items = serializer.validated_data.get("items")

        # Подчёт количества повторяющихся товаров и конвертация в dict
        items_counter = convert_list_items_for_count_dict(items)
        id_items = list(items_counter.keys())

        # Получение Items из бд и проверка их существования
        try:
            items_objects = get_items_by_ids(id_items)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        # Формирование списка для шаблонизатора
        data = []
        for item in items_objects:
            data.append({
                "id": item.pk,
                "title": item.title,
                "price": item.price,
                "count": items_counter[item.pk],
            })

        # Создание PDF чека из шаблона
        url_check = create_check(data, date_obj=datetime.now(), save_path=settings.MEDIA_ROOT)

        full_url = f"http://{request.META['HTTP_HOST']}/{url_check}"

        qr = create_qr_for_url(full_url)
        # Создание буфера в памяти
        buffer = io.BytesIO()
        # Сохранение изображения в буфер
        qr.save(buffer, format='PNG')
        buffer.seek(0)

        return FileResponse(buffer, content_type='image/png')





