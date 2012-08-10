Ext.application({
    name: 'core',
    appFolder: 'static/app',
    autoCreateViewport: true,
    controllers: [
        'Canvas',
        'Sessions',
    ],
    launch: function() {
        console.log('App launch');
        return true;
    },
});
