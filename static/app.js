Ext.application({
    name: 'core',
    appFolder: 'static/app',
    autoCreateViewport: true,
    controllers: [
        'Canvas',
    ],
    launch: function() {
        console.log('App launch');
    },
});
