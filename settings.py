from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from deepmerge import always_merger

def extend_superapp_settings(main_settings):
    main_settings['INSTALLED_APPS'] = [
        'superapp.apps.backups',
    ] + main_settings['INSTALLED_APPS']


    main_settings.update(
        always_merger.merge(
            {
                'BACKUPS': {
                    'BACKUP_TYPES': {
                        'all_models': {
                            'name': _('All Models'),
                            'description': _('Backup all models'),
                            'models': '*',
                            'exclude_models_from_import': [],
                        },
                    },
                }
            },
            main_settings,
        )
    )
    main_settings['UNFOLD']['SIDEBAR']['navigation'] += [
        {
            "title": _("Backups"),
            "icon": "database",
            "items": [
                {
                    "title": _("Backups"),
                    "icon": "backup",
                    "link": reverse_lazy("admin:backups_backup_changelist"),
                    "permission": lambda request: request.user.has_perm('backups.view_backup'),
                },
                {
                    "title": _("Restores"),
                    "icon": "restart_alt",
                    "link": reverse_lazy("admin:backups_restore_changelist"),
                    "permission": lambda request: request.user.has_perm('backups.view_restore'),
                },
            ]
        }
    ]

    # Configure Celery Beat schedule for backup tasks
    import os
    setup_scheduled_tasks = os.getenv('SETUP_SCHEDULED_TASKS', 'true').lower() == 'true'
    
    if setup_scheduled_tasks:
        from celery.schedules import crontab
        
        # Initialize CELERY_BEAT_SCHEDULE if it doesn't exist
        if 'CELERY_BEAT_SCHEDULE' not in main_settings:
            main_settings['CELERY_BEAT_SCHEDULE'] = {}
        
        # Add backup tasks
        main_settings['CELERY_BEAT_SCHEDULE'].update({
            'backups-weekly-essential-backup': {
                'task': 'backups.automated_weekly_backup',
                'schedule': crontab(hour=3, minute=0, day_of_week=1),  # Weekly on Monday at 3 AM
            },
        })
