from models import Alert


NEXT_STEPS = {
    "critical": "Investigate immediately and take corrective action.",
    "warning": "Review the affected system and monitor the metric closely.",
    "info": "Review the metric and confirm whether any action is needed.",
}


def generate_explanation(alert: Alert) -> str:
    """Build a plain-language explanation of an alert.

    Compares the alert's metric value with its threshold, then describes the
    result as "exceeded", "fell below", or "reached". Adds the recommended next
    step from ``NEXT_STEPS`` for the alert's severity. Finally, adds an
    "Acknowledged by" note. The note uses the alert's optional ``resolved_by``
    attribute in uppercase. If that attribute is missing or ``None``, the note
    says "Not yet acknowledged".

    Args:
        alert: The alert to explain. Its ``severity``, ``source``, ``title``,
            ``metric_name``, ``metric_value``, and ``threshold`` attributes
            are read.

    Returns:
        The explanation as a single string.

    Raises:
        KeyError: If ``alert.severity`` is not "critical", "warning", or
            "info".
    """
    if alert.metric_value > alert.threshold:
        comparison = "exceeded"
    elif alert.metric_value < alert.threshold:
        comparison = "fell below"
    else:
        comparison = "reached"

    next_step = NEXT_STEPS[alert.severity]
    explanation = (
        f'This {alert.severity} alert from {alert.source} is titled "{alert.title}". '
        f"The {alert.metric_name} metric {comparison} its threshold: the current value is "
        f"{alert.metric_value}, compared with a threshold of {alert.threshold}. "
        f"Recommended next step: {next_step}"
    )
    resolved_by = getattr(alert, "resolved_by", None) 
    acknowledged_by = (
        resolved_by.upper() if resolved_by is not None else "Not yet acknowledged"
    )
    return explanation + f" Acknowledged by: {acknowledged_by}."