Ext.define('core.view.session.Select', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.sessionSelect',
    layout: 'hbox',
    items: [{
        xtype: 'combobox',
        emptyText: 'Select a session',
        store: 'Sessions',
        displayField: 'name',
        valueField: 'id',
        editable: false,
        width: 125,
        height: null,
    }, {
        xtype: 'button',
        tooltip: 'New Session',
        itemId: 'new-session',
        width: 24,
        height: 24,
        componentCls: 'palette palette-new-session',
        enableToggle: false,
        toggleGroup: null,
    }],
});
