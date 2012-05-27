//Ext.require('core.proxy.Rest');

Ext.define('core.model.Node', {
    extend: 'Ext.data.Model',
    fields: ['id', 'name', 'type'],
    associations: [{
        type: 'belongsTo',
        model: 'core.model.Session',
        getterName: 'getSession',
        setterName: 'setSession',
    }],

    constructor: function() {
        var model = this;

        Ext.override(this.proxy, {
            buildUrl: function(request) {
                var url = Ext.data.proxy.Rest.prototype.buildUrl.apply(
                    this, arguments);

                var sessionId = model.get('core.model.session_id');
                //console.log('Model:', model);
                //console.log('Session ID: "' + sessionId + '"', sessionId === '', sessionId !== '');

                if (sessionId !== '') {
                    url = '/sessions/' + sessionId + url;
                }
                console.log('URL:', url);
                return url;
            },
        });

        this.callParent(arguments);
    },

    proxy: {
        type: 'rest',
        url: '/nodes/',
        reader: {
            type: 'json',
        },
        writer: {
            type: 'json',
        },
    },
});
