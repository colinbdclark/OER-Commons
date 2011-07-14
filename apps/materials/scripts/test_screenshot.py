

def run():
    from materials.models import Course
    from materials.tasks import update_screenshot

    item = Course.objects.filter(http_status=200)[0]

    update_screenshot(item)