Ext.define('core.store.Nodes', {
    extend: 'Ext.data.Store',
    autoLoad: false,
    model: 'core.model.Node',
    storeId: 'nodeStore',
});
