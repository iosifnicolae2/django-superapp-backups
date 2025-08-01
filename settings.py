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
                        'essential_data': {
                            'name': _('Essential Data'),
                            'description': _('Backup essential data only'),
                            'models': [
                                'my_app.essential_model',
                            ],
                            'exclude_models_from_import': [],
                            'exclude_fields': {
                                'my_app.essential_model': ['user',],
                            },
                            'schedule': {
                                'enabled': True,
                                'hour': 3,
                                'minute': 0,
                                'day_of_week': 1,  # Monday
                            },
                        },
                    },
                    'RETENTION': {
                        'MAX_BACKUPS': 30,
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

    # Configure backup schedules
    from .schedule import setup_backup_schedules
    setup_backup_schedules(main_settings)

