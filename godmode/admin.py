from dataclasses import dataclass, field
from typing import Callable

from typing_extensions import Optional

from django import forms
from django.db import models
from django.template.loader import render_to_string

from users.models.user import User


# Common field name -> Russian label, applied across all forms. Per-model `field_labels` overrides.
GLOBAL_FIELD_LABELS = {
    "slug": "Идентификатор (slug)",
    "title": "Заголовок",
    "subtitle": "Подзаголовок",
    "full_name": "Имя",
    "email": "Email",
    "avatar": "Аватар (URL)",
    "company": "Компания",
    "position": "Должность",
    "city": "Город",
    "country": "Страна",
    "bio": "О себе",
    "contact": "Контакты",
    "description": "Описание",
    "text": "Текст",
    "url": "Ссылка",
    "image": "Картинка (URL)",
    "icon": "Иконка / эмодзи",
    "color": "Цвет (hex)",
    "type": "Тип",
    "author": "Автор",
    "room": "Комната",
    "visibility": "Видимость",
    "label_code": "Лейбл",
    "collectible_tag_code": "Коллекционный тег",
    "coauthors": "Соавторы",
    "comment_template": "Шаблон комментария",
    "published_at": "Опубликован (дата)",
    "is_room_only": "Только для комнаты",
    "is_public": "Публичный",
    "is_pinned_until": "Закреплён до",
    "is_visible": "Показывать",
    "is_pinned": "Закреплён",
    "is_commentable": "Можно комментировать",
    "is_open_for_posting": "Открыта для постинга",
    "moderation_status": "Статус модерации",
    "is_email_verified": "Email подтверждён",
    "is_email_unsubscribed": "Отписан от рассылок",
    "is_banned_until": "Забанен до",
    "deleted_at": "Удалён (дата)",
    "profile_publicity_level": "Публичность профиля",
    "email_digest_type": "Тип дайджеста",
    "year_of_graduation": "Год выпуска",
    "faculty": "Факультет",
    "telegram_id": "Telegram ID",
    "chat_name": "Название чата",
    "chat_url": "Ссылка на чат",
    "chat_id": "ID чата в Telegram",
    "send_new_posts_to_chat": "Слать новые посты в чат",
    "send_new_comments_to_chat": "Слать комменты в чат",
    "network_group": "Группа карты-сети",
    # auto-managed / internal fields (visible, but labelled so it's clear they're service fields)
    "upvotes": "Плюсы (счётчик)",
    "hotness": "Горячесть (счётчик)",
    "view_count": "Просмотры (счётчик)",
    "comment_count": "Комментарии (счётчик)",
    "vote_count": "Голоса (счётчик)",
    "chat_member_count": "Участников в чате (счётчик)",
    "last_activity_at": "Последняя активность",
    "last_view_at": "Последний просмотр",
    "created_at": "Создано",
    "updated_at": "Обновлено",
    "published_at_date": "Дата публикации",
    "html": "HTML-кеш",
    "metadata": "Метаданные (JSON)",
    "telegram_data": "Данные Telegram (JSON)",
    "geo": "Геолокация",
    "hat": "Шапка (JSON)",
    "style": "CSS-стиль",
    "index": "Порядок сортировки",
    "secret_hash": "Секретный хеш",
    # relations / remaining fields across comments, badges, tags, invites, geo, achievements, settings
    "post": "Пост",
    "comment": "Комментарий",
    "reply_to": "Ответ на",
    "user": "Юзер",
    "from_user": "От кого",
    "to_user": "Кому",
    "user_from": "Юзер (от)",
    "user_to": "Юзер (кому)",
    "badge": "Бейдж",
    "achievement": "Ачивка",
    "tag": "Тег",
    "note": "Примечание",
    "code": "Код",
    "name": "Название",
    "value": "Значение",
    "group": "Группа",
    "is_deleted": "Удалён",
    "deleted_by": "Кем удалён",
    "ipaddress": "IP-адрес",
    "useragent": "User-Agent",
    "invited_email": "Email приглашённого",
    "invited_user": "Приглашённый юзер",
    "used_at": "Использован (дата)",
    "is_subscribed_to_posts": "Подписан на посты",
    "is_subscribed_to_comments": "Подписан на комментарии",
    "post_from": "Пост (откуда)",
    "post_to": "Пост (куда)",
    "custom_message": "Своё сообщение",
    "custom_template": "Свой шаблон",
    "latitude": "Широта",
    "longitude": "Долгота",
    "population": "Население",
    "region": "Регион",
    "city_en": "Город (англ.)",
    "country_en": "Страна (англ.)",
    "region_en": "Регион (англ.)",
}

# Help text for non-obvious fields, applied across all forms. Per-model `field_help` overrides.
GLOBAL_FIELD_HELP = {
    "slug": "Короткий идентификатор для URL — латиница и дефисы",
    "color": "Цвет в hex, например #4CAF50",
    "icon": "Эмодзи или HTML-иконка рядом с названием",
    "moderation_status": "intro / on_review / approved / rejected / deleted",
    "visibility": "draft / link_only / everywhere",
    "is_banned_until": "Дата окончания бана. Пусто — не забанен",
    "chat_id": "Числовой ID чата — нужен боту для отправки сообщений (узнать: @getidsbot в чате)",
    "chat_url": "Инвайт-ссылка на чат (https://t.me/…)",
    "send_new_posts_to_chat": "Авто-постинг новых постов комнаты в привязанный Telegram-чат",
    "network_group": "ID группы на карте-сети, если комната к ней относится",
    # warn that these are auto-managed — usually shouldn't be edited by hand
    "upvotes": "Служебный счётчик, обновляется автоматически",
    "hotness": "Служебный рейтинг для сортировки, считается автоматически",
    "view_count": "Служебный счётчик, обновляется автоматически",
    "comment_count": "Служебный счётчик, обновляется автоматически",
    "chat_member_count": "Обновляется ботом автоматически",
    "html": "Кеш отрендеренного текста, генерится автоматически из поля «Текст»",
    "metadata": "Служебное JSON-поле, обычно трогать не нужно",
    "telegram_data": "Сырой ответ от Telegram, служебное",
    "style": "Служебное CSS-оформление",
    "index": "Чем меньше число — тем выше в списке",
    "secret_hash": "Служебный секрет для ссылок, не менять",
}


@dataclass
class ClubAdminField:
    name: str
    display_name: str
    model_field: Optional[models.Field] = None
    list_template: Optional[str] = None

    @classmethod
    def from_model_field(cls, model_field: models.Field):
        return cls(
            name=model_field.name or "Unknown",
            display_name=model_field.verbose_name or model_field.name.replace("_", " ").title(),
            model_field=model_field,
        )

    def render_list(self, value):
        if self.list_template:
            return render_to_string(self.list_template, {
                "value": value,
            })

        try:
            if value is None:
                return ""
            elif hasattr(value, 'strftime'):  # Date/DateTime fields
                return value.strftime('%Y-%m-%d %H:%M')
            elif isinstance(value, bool):
                return "✅" if value else "❌"
            elif hasattr(value, '__str__'):
                # Truncate long values
                str_value = str(value)
                if len(str_value) > 150:
                    str_value = str_value[:150] + "..."
                return str_value
            else:
                return str(value)
        except Exception:
            return "???"


@dataclass
class ClubAdminAction:
    title: str = None
    get: Callable = None
    post: Callable = None

    access_roles: set[str] = field(default_factory=lambda: {User.ROLE_MODERATOR, User.ROLE_GOD})

    def has_access(self, user: User) -> bool:
        return bool(set(user.roles or []) & set(self.access_roles or []))


@dataclass
class ClubAdminModel:
    model: type[models.Model] = None
    title: str = None
    icon: str = None
    name: str = None
    title_field: str = None

    list_fields: list | ClubAdminField = field(default_factory=list)
    edit_fields: list = field(default_factory=list)
    hide_fields: list = field(default_factory=list)
    field_labels: dict = field(default_factory=dict)
    field_help: dict = field(default_factory=dict)

    list_roles: set[str] = field(default_factory=lambda: {User.ROLE_MODERATOR, User.ROLE_GOD})
    edit_roles: set[str] = field(default_factory=lambda: {User.ROLE_MODERATOR, User.ROLE_GOD})
    create_roles: set[str] = field(default_factory=lambda: {User.ROLE_GOD})
    delete_roles: set[str] = field(default_factory=lambda: {User.ROLE_GOD})

    actions: dict[str, ClubAdminAction] = field(default_factory=dict)

    def get_absolute_url(self):
        return f"/godmode/{self.name}/" if self.name else None

    def has_list_access(self, user: User) -> bool:
        return bool(set(user.roles or []) & set(self.list_roles or []))

    def has_edit_access(self, user: User) -> bool:
        return bool(set(user.roles or []) & set(self.edit_roles or []))

    def has_create_access(self, user: User) -> bool:
        return bool(set(user.roles or []) & set(self.create_roles or []))

    def has_delete_access(self, user: User) -> bool:
        return bool(set(user.roles or []) & set(self.delete_roles or []))

    def get_list_fields(self):
        fields = []
        if self.list_fields:
            for field in self.list_fields:
                if isinstance(field, ClubAdminField):
                    field.model_field = self.model._meta.get_field(field.name)
                    fields.append(field)
                else:
                    fields.append(ClubAdminField.from_model_field(self.model._meta.get_field(field)))
        else:
            fields = [
                ClubAdminField.from_model_field(field)
                for field in self.model._meta.fields
                if field.name not in self.hide_fields
            ]
        return fields

    def get_form_class(self):
        admin_model = self

        labels = {**GLOBAL_FIELD_LABELS, **admin_model.field_labels}
        help_texts = {**GLOBAL_FIELD_HELP, **admin_model.field_help}

        class DynamicModelForm(forms.ModelForm):
            class Meta:
                model = admin_model.model
                fields = admin_model.edit_fields if admin_model.edit_fields else [
                    field.name for field in admin_model.model._meta.fields
                    if field.editable and field.name not in admin_model.hide_fields
                ]

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                for field_name, field in self.fields.items():
                    model_field = admin_model.model._meta.get_field(field_name)

                    # Russian label + help text (global, with per-model overrides)
                    if field_name in labels:
                        field.label = labels[field_name]
                    if field_name in help_texts:
                        field.help_text = help_texts[field_name]

                    # Handle foreign key fields - show PK in a text input
                    if isinstance(model_field, models.ForeignKey):
                        field.widget = forms.TextInput()
                        # Set the display value to the related object"s string representation
                        if self.instance and self.instance.pk:
                            related_obj = getattr(self.instance, field_name, None)
                            if related_obj:
                                field.initial = related_obj.pk

                    # Set required based on model constraints
                    if not model_field.null and not model_field.blank and not model_field.has_default():
                        field.required = True
                    else:
                        field.required = False
        return DynamicModelForm


@dataclass
class ClubAdminPage:
    title: str = None
    icon: str = None
    name: str = None

    access_roles: set[str] = field(default_factory=lambda: {User.ROLE_MODERATOR, User.ROLE_GOD})

    view: Callable = None

    def get_absolute_url(self):
        return f"/godmode/page/{self.name}/" if self.name else None

    def has_access(self, user: User) -> bool:
        return bool(set(user.roles or []) & set(self.access_roles or []))


@dataclass
class ClubAdminGroup:
    title: str = "Default Group"
    icon: str = ""
    models: list[ClubAdminModel | ClubAdminPage] = field(default_factory=list)


@dataclass
class ClubAdmin:
    title: str = "Admin"
    groups: list[ClubAdminGroup] = field(default_factory=list)
    foreign_key_templates: dict = field(default_factory=dict)

    access_roles: set[str] = field(default_factory=lambda: {User.ROLE_CURATOR, User.ROLE_MODERATOR, User.ROLE_GOD})

    def get_model(self, model_name: str) -> ClubAdminModel | None:
        for group in self.groups:
            for model in group.models:
                if isinstance(model, ClubAdminModel) and model.name == model_name:
                    return model
        return None

    def get_page(self, page_name: str) -> ClubAdminPage | None:
        for group in self.groups:
            for model in group.models:
                if isinstance(model, ClubAdminPage) and model.name == page_name:
                    return model
        return None


    def has_access(self, user: User) -> bool:
        return bool(set(user.roles or []) & set(self.access_roles or []))

