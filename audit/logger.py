import logging

logger = logging.getLogger('audit')


def log_event(event_type, user, object_type, object_id, detail='', request=None):
    ip = 'unknown'
    if request:
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded.split(',')[0] if x_forwarded else request.META.get('REMOTE_ADDR', 'unknown')

    logger.info(
        f"EVENT={event_type} | "
        f"USER={user.username} (id={user.pk}) | "
        f"IP={ip} | "
        f"OBJECT={object_type}:{object_id} | "
        f"DETAIL={detail}"
    )