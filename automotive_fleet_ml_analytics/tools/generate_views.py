#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo Interactive UI Generator
User can select: Views, Wizard, Actions, Menu
Saves to: Generated/ folder
File: tools/generate_views.py
Run: python tools/generate_views.py
"""

import re
import os

class OdooInteractiveGenerator:

    def __init__(self, model_file_path):
        self.model_file_path = model_file_path
        self.model_name = None
        self.model_label = None
        self.fields_data = []
        self.options = {}

    def extract_fields(self):
        """Extract model name and all fields from Python file"""
        with open(self.model_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        name_match = re.search(r"_name\s*=\s*['\"]([^'\"]+)['\"]", content)
        self.model_name = name_match.group(1) if name_match else "model.name"

        desc_match = re.search(r"_description\s*=\s*['\"]([^'\"]+)['\"]", content)
        self.model_label = desc_match.group(1) if desc_match else self.model_name.replace('.', ' ').title()

        field_pattern = r"(\w+)\s*=\s*fields\.(\w+)\((.*?)\)"
        matches = re.finditer(field_pattern, content, re.DOTALL)

        for match in matches:
            field_name = match.group(1)
            field_type = match.group(2)
            field_attrs = match.group(3)

            if field_name.startswith('_'):
                continue

            string_match = re.search(r"string=['\"]([^'\"]+)['\"]", field_attrs)
            label = string_match.group(1) if string_match else field_name.replace('_', ' ').title()

            is_required = 'required=True' in field_attrs
            is_compute = 'compute=' in field_attrs
            is_readonly = 'readonly=True' in field_attrs or is_compute
            is_text = field_type in ['Text', 'Html']
            is_selection = field_type == 'Selection'
            is_many2one = field_type == 'Many2one'

            self.fields_data.append({
                'name': field_name,
                'label': label,
                'type': field_type,
                'required': is_required,
                'compute': is_compute,
                'readonly': is_readonly,
                'is_text': is_text,
                'is_selection': is_selection,
                'is_many2one': is_many2one,
            })

        return self.model_name, self.model_label, self.fields_data

    def group_three_way(self):
        """Group fields: 1.Required 2.Optional 3.Computed"""
        group_required = []
        group_optional = []
        group_computed = []

        for field in self.fields_data:
            if field['compute'] or field['readonly']:
                group_computed.append(field)
            elif field['required']:
                group_required.append(field)
            else:
                group_optional.append(field)

        return group_required, group_optional, group_computed

    def show_interactive_menu(self):
        """Show menu and get user selection"""
        print(f"\n{'='*60}")
        print(f"🎯 ODOO UI GENERATOR - {self.model_label}")
        print(f"{'='*60}")
        print(f"Model: {self.model_name}")
        print(f"Fields Found: {len(self.fields_data)}")
        print(f"{'='*60}\n")

        print("📋 SELECT WHAT TO GENERATE:")
        print(f"{'-'*60}")

        # Views Selection
        print("\n1️⃣ VIEWS:")
        self.options['form'] = self.ask_yes_no(" Generate FORM VIEW?", default=True)
        self.options['tree'] = self.ask_yes_no(" Generate TREE VIEW?", default=True)
        self.options['kanban'] = self.ask_yes_no(" Generate KANBAN VIEW?", default=False)
        self.options['search'] = self.ask_yes_no(" Generate SEARCH VIEW?", default=True)

        # Advanced Options
        print("\n2️⃣ ADVANCED:")
        self.options['wizard'] = self.ask_yes_no(" Generate WIZARD?", default=False)
        self.options['action'] = self.ask_yes_no(" Generate ACTION?", default=True)
        self.options['menu'] = self.ask_yes_no(" Generate MENU ITEM?", default=True)

        # Menu Parent
        if self.options['menu']:
            print("\n3️⃣ MENU CONFIGURATION:")
            parent = input(" Parent Menu [Leave empty for top level]: ").strip()
            self.options['menu_parent'] = parent if parent else None
            seq = input(" Menu Sequence [Default: 10]: ").strip()
            self.options['menu_sequence'] = seq if seq else "10"

        # Grouping Style
        print("\n4️⃣ FORM LAYOUT:")
        print(" 1. Three-Way Grouping (Required → Optional → Computed)")
        print(" 2. Simple Grouping (All fields together)")
        layout = input(" Select layout [1]: ").strip()
        self.options['three_way_grouping'] = layout!= "2"

        print(f"\n{'='*60}")
        print("✅ CONFIGURATION COMPLETE!")
        print(f"{'='*60}\n")

    def ask_yes_no(self, question, default=True):
        """Ask yes/no question"""
        default_str = "Y/n" if default else "y/N"
        answer = input(f"{question} [{default_str}]: ").strip().lower()
        if not answer:
            return default
        return answer in ['y', 'yes']

    def generate_xml(self):
        """Generate XML based on user selection"""
        self.extract_fields()
        self.show_interactive_menu()

        g_req, g_opt, g_comp = self.group_three_way()
        model_short = self.model_name.replace('.', '_')
        model_name = self.model_name
        model_label = self.model_label

        xml = f'''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>

'''
        # ========== FORM VIEW ==========
        if self.options['form']:
            xml += f''' <!-- ========== FORM VIEW ========== -->
        <record id="view_{model_short}_form" model="ir.ui.view">
            <field name="name">{model_name}.form</field>
            <field name="model">{model_name}</field>
            <field name="arch" type="xml">
                <form string="{model_label}">
                    <sheet>
'''
            if self.options['three_way_grouping']:
                # Three-way grouping
                if g_req:
                    xml += ''' <group string="Required Information">
                            <group>
'''
                    for field in g_req:
                        xml += f' <field name="{field["name"]}" required="1"/>\n'
                    xml += ''' </group>
                        </group>
'''
                if g_opt:
                    xml += ''' <group string="Additional Information">
                            <group>
'''
                    for field in g_opt:
                        if not field['is_text']:
                            xml += f' <field name="{field["name"]}"/>\n'
                    xml += ''' </group>
                        </group>
'''
                    text_fields = [f for f in g_opt if f['is_text']]
                    if text_fields:
                        xml += ''' <group string="Notes">
'''
                        for field in text_fields:
                            xml += f' <field name="{field["name"]}" placeholder="{field["label"]}..."/>\n'
                        xml += ''' </group>
'''
                if g_comp:
                    xml += ''' <group string="Computed Data" attrs="{'invisible': [('id', '=', False)]}">
                            <group>
'''
                    for field in g_comp:
                        xml += f' <field name="{field["name"]}" readonly="1"/>\n'
                    xml += ''' </group>
                        </group>
'''
            else:
                # Simple grouping
                xml += ''' <group>
                            <group>
'''
                for field in g_req + g_opt:
                    xml += f' <field name="{field["name"]}"/>\n'
                xml += ''' </group>
                        </group>
'''

            xml += ''' </sheet>
                </form>
            </field>
        </record>

'''

        # ========== TREE VIEW ==========
        if self.options['tree']:
            xml += f''' <!-- ========== TREE VIEW ========== -->
        <record id="view_{model_short}_tree" model="ir.ui.view">
            <field name="name">{model_name}.tree</field>
            <field name="model">{model_name}</field>
            <field name="arch" type="xml">
                <tree string="{model_label}">
'''
            tree_fields = g_req + [f for f in g_opt if not f['is_text']][:4]
            for field in tree_fields:
                xml += f' <field name="{field["name"]}"/>\n'
            xml += ''' </tree>
            </field>
        </record>

'''

        # ========== KANBAN VIEW ==========
        if self.options['kanban']:
            xml += f''' <!-- ========== KANBAN VIEW ========== -->
        <record id="view_{model_short}_kanban" model="ir.ui.view">
            <field name="name">{model_name}.kanban</field>
            <field name="model">{model_name}</field>
            <field name="arch" type="xml">
                <kanban>
'''
            kanban_fields = g_req[:2] + g_opt[:2]
            for field in kanban_fields:
                xml += f' <field name="{field["name"]}"/>\n'
            xml += ''' <templates>
                        <t t-name="kanban-box">
                            <div class="oe_kanban_global_click">
                                <div class="oe_kanban_details">
'''
            for field in kanban_fields:
                xml += f' <div><strong>{field["label"]}:</strong> <field name="{field["name"]}"</div>\n'
            xml += ''' </div>
                            </div>
                        </t>
                    </templates>
                </kanban>
            </field>
        </record>

'''

        # ========== SEARCH VIEW ==========
        if self.options['search']:
            xml += f''' <!-- ========== SEARCH VIEW ========== -->
        <record id="view_{model_short}_search" model="ir.ui.view">
            <field name="name">{model_name}.search</field>
            <field name="model">{model_name}</field>
            <field name="arch" type="xml">
                <search string="{model_label}">
'''
            search_fields = [f for f in g_req + g_opt if f['is_many2one'] or f['is_selection']][:3]
            for field in search_fields:
                xml += f' <field name="{field["name"]}"/>\n'

            if any(f['is_selection'] for f in self.fields_data):
                xml += ''' <separator/>
'''
                for field in [f for f in self.fields_data if f['is_selection']][:2]:
                    xml += f' <filter string="{field["label"]}" name="filter_{field["name"]}" domain="[('{field["name"]}','!=',False)]"/>\n'

            if any(f['is_many2one'] for f in self.fields_data):
                xml += ''' <group expand="0" string="Group By">
'''
                for field in [f for f in self.fields_data if f['is_many2one']][:2]:
                    xml += f' <filter string="{field["label"]}" name="group_{field["name"]}" context="{{'group_by': '{field["name"]}'}}"/>\n'
                xml += ''' </group>
'''
            xml += ''' </search>
            </field>
        </record>

'''

        # ========== WIZARD ==========
        if self.options['wizard']:
            xml += f''' <!-- ========== WIZARD ========== -->
        <record id="wizard_{model_short}_form" model="ir.ui.view">
            <field name="name">{model_name}.wizard.form</field>
            <field name="model">{model_name}</field>
            <field name="arch" type="xml">
                <form string="{model_label} Wizard">
                    <sheet>
                        <group>
                            <group>
'''
            for field in g_req[:3]: # First 3 required fields
                xml += f' <field name="{field["name"]}" required="1"/>\n'
            xml += ''' </group>
                        </group>
                    </sheet>
                    <footer>
                        <button string="Confirm" type="object" name="action_confirm" class="btn-primary"/>
                        <button string="Cancel" class="btn-secondary" special="cancel"/>
                    </footer>
                </form>
            </field>
        </record>

'''

        # ========== ACTION ==========
        if self.options['action']:
            view_modes = []
            if self.options['kanban']: view_modes.append('kanban')
            if self.options['tree']: view_modes.append('tree')
            if self.options['form']: view_modes.append('form')
            view_mode_str = ','.join(view_modes) if view_modes else 'tree,form'

            xml += f''' <!-- ========== ACTION ========== -->
        <record id="action_{model_short}" model="ir.actions.act_window">
            <field name="name">{model_label}</field>
            <field name="res_model">{model_name}</field>
            <field name="view_mode">{view_mode_str}</field>
'''
            if self.options['search']:
                xml += f' <field name="search_view_id" ref="view_{model_short}_search"/>\n'

            xml += f''' <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Create your first {model_label}
                </p>
            </field>
        </record>

'''

        # ========== MENU ITEM ==========
        if self.options['menu']:
            menu_attrs = f'id="menu_{model_short}" name="{model_label}" action="action_{model_short}"'
            if self.options.get('menu_parent'):
                menu_attrs += f' parent="{self.options["menu_parent"]}"'
            menu_attrs += f' sequence="{self.options.get("menu_sequence", "10")}"'

            xml += f''' <!-- ========== MENU ITEM ========== -->
        <menuitem {menu_attrs}/>

'''

        xml += ''' </data>
</odoo>
'''

        # ===== SAVE TO Generated/ FOLDER =====
        addon_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        generated_dir = os.path.join(addon_root, 'Generated')
        os.makedirs(generated_dir, exist_ok=True)

        filename = f"{model_short}_views.xml"
        filepath = os.path.join(generated_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml)

        # Print summary
        print(f"\n{'='*60}")
        print(f"✅ GENERATED SUCCESSFULLY")
        print(f"{'='*60}")
        print(f"📄 File: {filepath}")
        print(f"\n📊 GENERATED COMPONENTS:")
        if self.options['form']: print(f" ✅ FORM VIEW")
        if self.options['tree']: print(f" ✅ TREE VIEW")
        if self.options['kanban']: print(f" ✅ KANBAN VIEW")
        if self.options['search']: print(f" ✅ SEARCH VIEW")
        if self.options['wizard']: print(f" ✅ WIZARD")
        if self.options['action']: print(f" ✅ ACTION")
        if self.options['menu']: print(f" ✅ MENU ITEM")

        print(f"\n{'='*60}")
        print(f"📋 NEXT STEPS:")
        print(f"{'='*60}")
        print(f" 1. Review: cat {filepath}")
        print(f" 2. Move: mv {filepath} views/")
        print(f" 3. Update manifest: Add 'views/{filename}' to data")
        print(f" 4. Upgrade: odoo -u your_addon")
        print(f"{'='*60}\n")

        return filepath

# ===== RUN THIS =====
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 ODOO INTERACTIVE UI GENERATOR")
    print("="*60)

    # Get model path from user
    model_path = input("\n📁 Enter model file path [models/ml_prediction.py]: ").strip()
    if not model_path:
        model_path = "models/ml_prediction.py"

    if not os.path.exists(model_path):
        print(f"\n❌ ERROR: File not found: {model_path}")
        exit(1)

    generator = OdooInteractiveGenerator(model_path)
    generator.generate_xml()