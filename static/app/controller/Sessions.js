Ext.define('core.controller.Sessions', {
    extend: 'Ext.app.Controller',
    views: [
        'session.New',
        'session.Select',
    ],
    stores: [
        'Sessions',
    ],
    //refs: [
    //],

    init: function() {
        console.log('Sessions controller init');
        this.callParent(arguments);

        this.control({
            '[xtype="core.view.session.Select"]': {
                newSession: this.newSession,
            },
            //'core.view.Palette core.view.session.Select combobox': {
            //    select: this.selectSession,
            //},
            //'core.view.session.new #createSession': {
            //    click: this.createSession,
            //},
            //'core.view.session.new textfield': {
            //    specialkey: function(field, e) {
            //        if (e.getKey() == e.ENTER) {
            //            this.createSession(field);
            //        }
            //    }
            //},
        });
    },

    newSession: function() {
        console.log('New session');
    },
});
