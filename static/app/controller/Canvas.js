Ext.define('core.controller.Canvas', {
    extend: 'Ext.app.Controller',
    views: [
        'Canvas',
        'Palette',
    ],
    stores: [
        'Nodes',
    ],
    refs: [{
        selector: 'core.view.Canvas > draw',
        ref: 'draw',
    }, {
        selector: 'core.view.session.Select combobox',
        ref: 'sessionSelect',
    }],

    init: function() {
        console.log('Canvas controller init!');
        this.callParent(arguments);

        this.currentTool = null;

        this.control({
            'core.view.Canvas > draw': {
                click: this.canvasClick,
            },
            'core.view.Palette > buttongroup > button': {
                toggle: this.paletteToggle,
            },
        });
    },

    newSession: function(button, e) {
        var view = Ext.widget('core.view.session.new');
    },

    createSession: function(button) {
        console.log('CREATING SESSION');
        var win = button.up('window');
        var form = win.down('form');

        if (!form.getForm().isValid()) {
            return;
        }

        var values = form.getValues();
        var session = Ext.create('core.model.Session', values);

        var sessions = this.getSessionsStore();
        sessions.add(session);
        sessions.sync({
            scope: this,
            success: function() {
                var combobox = this.getSessionSelect();
                combobox.setValue(session);
                combobox.fireEvent('select', combobox, [session]);

                win.close();
            },
        });
    },

    selectSession: function(combobox, records) {
        console.log('select session');
        var session = records[0];
        var nodes = session.nodes();

        console.log('Nodes:', nodes);
    },

    createNode: function(node) {
        var select = this.getSessionSelect();
        var value = select.getValue();

        if (value === null) {
            return;
        }

        var session = select.findRecordByValue(value);
        var nodes = session.nodes();

        nodes.add(node);
        nodes.sync({
            scope: this,
            success: function() {
                console.log('Node created:', node);
                var draw = this.getDraw();
                var icon = draw.surface.add({
                    type: 'image',
                    src: '/static/resources/images/router.png',
                    x: node.get('x'),
                    y: node.get('y'),
                    width: 47,
                    height: 32,
                }).show(true);
            },
        });
    },

    canvasClick: function(e, t) {
        var draw = this.getDraw();
        var box = draw.getBox();

        var x = e.getX() - box.x;
        var y = e.getY() - box.y;

        switch (this.currentTool) {
            case 'select':
                break;
            case 'link':
                break;
            default:
                this.createNode(Ext.create('core.model.Node', {
                    type: this.currentTool,
                    x: x,
                    y: y,
                }));
        }
        /*
        var draw = this.getDraw();
        var box = draw.getBox();
        draw.surface.add({
            type: 'circle',
            fill: '#ff0000',
            radius: 100,
            x: e.getX() - box.x,
            y: e.getY() - box.y,
        }).show(true);
        */
    },

    paletteToggle: function(button, pressed) {
        if (pressed) {
            this.currentTool = button.coreType;
        } else {
            this.currentTool = null;
        }
    },
});
