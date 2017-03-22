from kivy.app import App
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.lang import Builder

from lbryum.i18n import _
from lbryum.util import base_units
from lbryum.i18n import languages, set_language
from lbryum.plugins import run_hook
from lbryum.lbrycrd import RECOMMENDED_FEE

Builder.load_string('''
#:import partial functools.partial

<SettingsItem@ButtonBehavior+BoxLayout>
    orientation: 'vertical'
    title: ''
    description: ''
    size_hint: 1, None

    canvas.before:
        Color:
            rgba: (0.192, .498, 0.745, 1) if self.state == 'down' else (0.3, 0.3, 0.3, 0)
        Rectangle:
            size: self.size
            pos: self.pos
    on_release:
        Clock.schedule_once(self.action)

    Label:
        id: title
        text: self.parent.title
        bold: True
        halign: 'left'
        size_hint: 1, 1
        text_size: self.width, None
    Label:
        text: self.parent.description
        color: 0.8, 0.8, 0.8, 1
        size_hint: 1, 1
        halign: 'left'
        text_size: self.width, None
    CardSeparator


<SettingsDialog@Popup>
    id: settings
    title: _('Electrum Settings')
    BoxLayout:
        orientation: 'vertical'
        ScrollView:
            size_hint: 1, 0.8
            GridLayout:
                row_default_height: '68dp'
                cols:1
                id: scrollviewlayout
                size_hint: 1, None
                SettingsItem:
                    lang: settings.get_language_name()
                    title: _('Language') + ': %s'%self.lang
                    description: _("Language")
                    action: partial(root.language_dialog, self)
                    height: '48dp'
                SettingsItem:
                    status: 'ON' if app.wallet.use_encryption else 'OFF'
                    title: _('PIN code') + ': ' + self.status
                    description: _("Change your PIN code.")
                    action: partial(root.change_password, self)
                SettingsItem:
                    bu: app.base_unit
                    title: _('Denomination') + ': ' + self.bu
                    description: _("Base unit for lbry amounts.")
                    action: partial(root.unit_dialog, self)
                SettingsItem:
                    status: root.fee_status()
                    title: _('Fees') + ': ' + self.status
                    description: _("Fees paid to the Lbry miners.")
                    action: partial(root.fee_dialog, self)
                SettingsItem:
                    status: root.fx_status()
                    title: _('Fiat Currency') + ': ' + self.status
                    description: _("Display amounts in fiat currency.")
                    action: partial(root.fx_dialog, self)
                SettingsItem:
                    status: 'ON' if bool(app.plugins.get('labels')) else 'OFF'
                    title: _('Labels Sync') + ': ' + self.status
                    description: "Synchronize labels."
                    action: partial(root.plugin_dialog, 'labels', self)
                SettingsItem:
                    title: _('OpenAlias')
                    description: "DNS record that stores one of your Lbry addresses."
                    action: partial(root.openalias_dialog, self)
        BoxLayout:
            size_hint: 1, 0.1
            Widget:
                size_hint: 0.5, None
            Button:
                size_hint: 0.5, None
                height: '48dp'
                text: _('OK')
                on_release:
                    settings.dismiss()
''')

class SettingsDialog(Factory.Popup):

    def __init__(self, app):
        self.app = app
        self.plugins = self.app.plugins
        self.config = self.app.electrum_config
        Factory.Popup.__init__(self)
        layout = self.ids.scrollviewlayout
        layout.bind(minimum_height=layout.setter('height'))

    def get_language_name(self):
        return languages.get(self.config.get('language', 'en_UK'), '')

    def change_password(self, label, dt):
        self.app.change_password()

    def language_dialog(self, item, dt):
        from choice_dialog import ChoiceDialog
        l = self.config.get('language', 'en_UK')
        def cb(key):
            self.config.set_key("language", key, True)
            item.lang = self.get_language_name()
            set_language(key)
        d = ChoiceDialog(_('Language'), languages, l, cb)
        d.open()

    def unit_dialog(self, item, dt):
        from choice_dialog import ChoiceDialog
        def cb(text):
            self.app._set_bu(text)
            item.bu = self.app.base_unit
        d = ChoiceDialog(_('Denomination'), base_units.keys(), self.app.base_unit, cb)
        d.open()

    def openalias_dialog(self, label, dt):
        from label_dialog import LabelDialog
        def callback(text):
            label.text = text
        d = LabelDialog(_('OpenAlias'), '', callback)
        d.open()

    def plugin_dialog(self, name, label, dt):
        from checkbox_dialog import CheckBoxDialog
        def callback(status):
            self.plugins.enable(name) if status else self.plugins.disable(name)
            label.status = 'ON' if status else 'OFF'

        status = bool(self.plugins.get(name))
        dd = self.plugins.descriptions.get(name)
        descr = dd.get('description')
        fullname = dd.get('fullname')
        d = CheckBoxDialog(fullname, descr, status, callback)
        d.open()

    def fee_status(self):
        if self.config.get('dynamic_fees'):
            f = self.config.get('fee_factor', 50) + 50
            return 'Dynamic, %d%%'%f
        else:
            F = self.config.get('fee_per_kb', RECOMMENDED_FEE)
            return self.app.format_amount_and_units(F) + '/kB'

    def fee_dialog(self, label, dt):
        from fee_dialog import FeeDialog
        def cb():
            label.status = self.fee_status()
        d = FeeDialog(self.app, self.config, cb)
        d.open()

    def fx_status(self):
        p = self.plugins.get('exchange_rate')
        if p:
            source = p.exchange.name()
            ccy = p.get_currency()
            return '%s [%s]' %(ccy, source)
        else:
            return 'Disabled'

    def fx_dialog(self, label, dt):
        from fx_dialog import FxDialog
        def cb():
            label.status = self.fx_status()
        d = FxDialog(self.app, self.plugins, self.config, cb)
        d.open()
