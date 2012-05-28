Ext.define('core.view.session.New', {
    extend: 'Ext.window.Window',
    alias: 'widget.sessionNew',
    title: 'New Session',
    layout: 'fit',
    autoShow: true,
    modal: true,
    items: [{
        xtype: 'form',
        itemId: 'form',
        url: '/sessions/',
        items: [{
            xtype: 'textfield',
            name: 'name',
            fieldLabel: 'Session Name',
            allowBlank: false,
        }, {
            xtype: 'textfield',
            name: 'user',
            fieldLabel: 'User Name',
            allowBlank: false,
        }],
        buttons: [{
            text: 'Create',
            itemId: 'createSession',
            action: 'save',
            formBind: true,
            disabled: true,
        }, {
            text: 'Cancel',
            itemId: 'cancel',
        }],
    }],
    onRender: function() {
        this.callParent(arguments);
        var buttonPanel = this.getComponent('form').getDockedItems()[0];

        var cancelButton = buttonPanel.getComponent('cancel');
        Ext.Object.merge(cancelButton, {scope: this, handler: this.close});
    },
    afterRender: function() {
        this.callParent(arguments);
        /* 200 is a delay for focusing, need to wait for the browser to render
         * the text box first.  This is terrible... */
        this.getComponent('form').query('textfield')[0].focus(true, 200);
    },
});
