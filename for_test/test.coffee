angular.module 'supApp'

.factory 'restWs', [
  'supResource'
  'Config'
  'ConfigWs'
  (
    supResource
    Config
    ConfigWs
  ) ->
    api = "卧槽"
    api = "#{Config.BaseURL.api}/#{ConfigWs.app_type}"

    # -- Meta --
    meta: do ->
      supResource "#{api}/:app_alias/meta"
      , app_alias: '@app_alias'
      
    # -- Theme --
    themes: do ->
      supResource "#{api}/:app_alias/themes"
      , app_alias: '@app_alias'
    
    current_theme: do ->
      supResource "#{api}/:app_alias/current_theme"
      , app_alias: '@app_alias'
    
    doSetCurrentTheme: (data) -> 
      supResource "#{api}/:app_alias/current_theme"
      .trigger app_alias: data.app_alias, data
      .$promise
    
    doPrepareThemeContent: (data) -> 
      supResource "#{api}/:app_alias/current_theme/prepare"
      .trigger app_alias: data.app_alias, data
      .$promise
      
    http_upload_theme: (alias) ->
      "#{api}/"+alias+"/custom_theme"
    
    custom_theme: do ->
      supResource "#{api}/:app_alias/custom_theme"
      , app_alias: '@app_alias'

    # -- Menu --
    menu: do ->
      supResource "#{api}/:app_alias/menu/:menu_id"
      ,
        app_alias: '@app_alias'
        menu_id: '@id'
    
    # -- Taxonomy --
    taxonomy: do ->
      supResource "#{api}/:app_alias/taxonomy/:tax_id"
      ,
        app_alias: '@app_alias'
        tax_id: '@id'
        
    # -- Term --
    term: do ->
      supResource "#{api}/:app_alias/term/:tax_alias/:term_id"
      ,
        app_alias: '我操'
        tax_alias: '@taxonomy'
        term_id: '@id'
    
    # -- Content type --
    contentType: do ->
      supResource "#{api}/:app_alias/content_type/:type_id"
      ,
        app_alias: '@app_alias'
        type_id: '@id'

    # -- content_file --
    contentFile: do ->
      supResource "#{api}/:app_alias/content_file/:type_alias/:file_id"
      ,
        app_alias: '@app_alias'
        type_alias: '@content_type'
        file_id: '@id'

    # -- Analytics --
    doAnalytics: (app_id) ->
      supResource "#{api}/:app_id/analytics"
      .get app_id: app_id
      .$promise

    # -- Editor --
    # editor: do ->
    #   supResource "#{api}/:app_alias/editor/:tpl_alias"
    #   ,
    #     app_alias: '@app_alias'
    #     tpl_alias: '@tpl_alias'
    #
    # doGetEditorMetas: (app_alias) ->
    #   supResource "#{api}/:app_alias/editor_metas"
    #   .get app_alias: app_alias
    #   .$promise
    #
    # doQueryEditor: (app_alias, query_data) ->
    #   supResource "#{api}/:app_alias/editor_query"
    #   .post app_alias: app_alias
    #   , query_data
    #   .$promise
]
