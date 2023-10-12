import os
from datetime import datetime
from collections import defaultdict

import qrcode

from cash_machine.models import Item
from jinja2 import Environment, FileSystemLoader
import pdfkit

from fictionalstore import settings


def convert_list_items_for_count_dict(items: list) -> dict[int]:
    """items = [1, 1, 1, 2, 2, 3] -> {1: 3, 2: 2, 3: 1}"""
    item_counts = defaultdict(int)
    for item in items:
        item_counts[item] += 1
    return dict(item_counts)


def get_items_by_ids(ids):
    items = Item.objects.filter(id__in=ids)
    if len(items) != len(ids):
        missing_ids = set(ids) - set(item.id for item in items)
        raise ValueError(f"Несуществует товаров с id: {missing_ids}")
    return items


def create_check(items: Item, date_obj: datetime) -> str:
    """
    Создаёт PDF и возвращает ссылку на него
    """
    data = {
        'date': date_obj.strftime("%H:%M"),
        'time': date_obj.strftime(f"%d.%m.%y"),
        'items': items,
        'total_price': sum(item['price'] * item['count'] for item in items),
    }
    lodaer = FileSystemLoader(settings.BASE_DIR /'cash_machine/template_for_pdf')
    env = Environment(loader=lodaer)
    tm = env.get_template('check.html')
    html_code = tm.render(data)
    path_wkhtmltopdf = str(settings.BASE_DIR / 'wkhtmltopdf/bin/wkhtmltopdf.exe')
    options = {
        'page-size': 'A6'}
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    file_check = f'check_{date_obj.strftime("%y-%m-%d__%H-%M-%S")}.pdf'
    output_path = str(settings.MEDIA_ROOT / file_check)

    pdfkit.from_string(html_code, output_path=output_path, configuration=config, options=options)
    return os.path.join(settings.MEDIA_URL, file_check)


def create_qr_for_url(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    return qr_img