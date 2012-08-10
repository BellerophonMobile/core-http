Ext.define('core.view.session.Select', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.core.view.session.Select',
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
        itemId: 'newButton',
        tooltip: 'New Session',
        width: 24,
        height: 24,
        componentCls: 'palette palette-new-session',
    }],
    initComponent: function() {
        this.callParent(arguments);
        this.addEvents('newSession');
        this.queryById('newButton').on('click', function() {
            this.fireEvent('newSession');
        }, this);
    }
});
