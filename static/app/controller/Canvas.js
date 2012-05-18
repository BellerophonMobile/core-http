Ext.define('core.controller.Canvas', {
    extend: 'Ext.app.Controller',
    views: [
        'Canvas',
        'Palette',
        'session.Select',
        'session.New',
    ],
    stores: [
        'Sessions',
        'Nodes',
    ],
    refs: [{
        selector: 'canvas > draw',
        ref: 'draw',
    }, {
        selector: 'sessionSelect',
        ref: 'sessionSelect',
    }],

    init: function() {
        this.callParent(arguments);
        console.log('Canvas controller init!');
        this.control({
            'canvas > draw': {
                click: this.canvasClick,
            },
            'palette > buttongroup > button': {
                toggle: this.paletteToggle,
            },
            'palette sessionSelect #new-session': {
                click: this.newSession,
            },
            'palette sessionSelect combobox': {
                select: this.selectSession,
            },
            'sessionNew #createSession': {
                click: this.createSession,
            },
        });
    },

    newSession: function(button, e) {
        var view = Ext.widget('sessionNew');
    },

    createSession: function(button) {
        var win = button.up('window');
        var values = win.down('form').getValues();

        var session = Ext.create('core.model.Session', values);
        this.getSessionsStore().add(session);

        var combobox = this.getSessionSelect().query('combobox')[0];
        combobox.select(session);
        combobox.fireEvent('select', combobox, [session]);

        win.close();
    },

    selectSession: function(combobox, records) {
        console.log('select session');
        var session = records[0];
        var nodes = session.nodes();

        var node = Ext.create('core.model.Node', {name: 'n0', type: 'wifi'});
        console.log('Add:', nodes.add(node));
        console.log('Sync:', nodes.sync());
    },

    canvasClick: function(e, t) {
        var draw = this.getDraw();
        var box = draw.getBox();
        draw.surface.add({
            type: 'circle',
            fill: '#ff0000',
            radius: 100,
            x: e.getX() - box.x,
            y: e.getY() - box.y,
        }).show(true);
    },

    paletteToggle: function(button, pressed) {
        console.log(button, pressed);
    },
});
