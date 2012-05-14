Ext.define('core.view.session.New', {
    extend: 'Ext.window.Window',
    alias: 'widget.session.new',
    title: 'New Session',
    layout: 'fit',
    autoShow: true,
    modal: true,
    items: [{
        xtype: 'form',
        items: [{
            xtype: 'textfield',
            name: 'name',
            fieldLabel: 'Session Name',
        }, {
            xtype: 'textfield',
            name: 'user',
            fieldLabel: 'User Name',
        }],
        buttons: [{
            text: 'Create',
        }, {
            text: 'Cancel',
            itemId: 'close',
        }],
    }],
    initComponent: function() {
        this.callParent(arguments);
        console.log(this.getComponent('close'));
    }
});
