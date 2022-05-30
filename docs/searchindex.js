Search.setIndex({docnames:["codesign","codesign.core","codesign.util","index","tests","tests.core","tests.util"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":5,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,sphinx:56},filenames:["codesign.rst","codesign.core.rst","codesign.util.rst","index.rst","tests.rst","tests.core.rst","tests.util.rst"],objects:{"":[[0,0,0,"-","codesign"],[4,0,0,"-","tests"]],"codesign.core":[[1,1,1,"","IS_LINUX"],[1,1,1,"","IS_MACOS"],[1,1,1,"","IS_RUNNING_AZURE_PIPELINE"],[1,1,1,"","IS_WINDOWS"],[1,0,0,"-","codesign"],[1,0,0,"-","codesign_config"]],"codesign.core.codesign":[[1,2,1,"","Codesign"]],"codesign.core.codesign.Codesign":[[1,3,1,"","codesign"],[1,4,1,"","config"],[1,3,1,"","lowercase_executable_name"],[1,3,1,"","pre_cleanup"],[1,3,1,"","remove_component_plugins"],[1,3,1,"","remove_php"],[1,3,1,"","remove_temp_files"],[1,3,1,"","run"],[1,3,1,"","sign_app"],[1,3,1,"","sign_bin_dir"],[1,3,1,"","sign_components"],[1,3,1,"","sign_contents"],[1,3,1,"","sign_database"],[1,3,1,"","sign_frameworks"],[1,3,1,"","sign_helpers"],[1,3,1,"","sign_internal_components"],[1,3,1,"","sign_mecab"],[1,3,1,"","sign_mobile"],[1,3,1,"","sign_native_components"],[1,3,1,"","sign_php"],[1,3,1,"","sign_plugins"],[1,3,1,"","sign_sasl_plugins"],[1,3,1,"","sign_updater"],[1,3,1,"","update_info_plist"]],"codesign.core.codesign_config":[[1,2,1,"","CodesignConfig"]],"codesign.core.codesign_config.CodesignConfig":[[1,4,1,"","default_hardened_runtime_entitlements"],[1,4,1,"","default_info_plist_properties"],[1,3,1,"","find_signing_identity"],[1,5,1,"","path_to_app_bundle"],[1,5,1,"","plist_data"],[1,4,1,"","runner_options"],[1,5,1,"","signing_identity"],[1,3,1,"","validate"]],"codesign.main":[[0,6,1,"","main"]],"codesign.util":[[2,0,0,"-","codesigning"],[2,0,0,"-","logging"],[2,0,0,"-","processes"]],"codesign.util.codesigning":[[2,6,1,"","convert_to_plist_format"],[2,6,1,"","create_entitlements_plist"],[2,6,1,"","remove_extended_attributes"],[2,6,1,"","run_codesign_command"],[2,6,1,"","run_codesign_command_for_hardened_runtime"],[2,6,1,"","run_install_name_tool"],[2,6,1,"","run_remove_codesign_command"]],"codesign.util.logging":[[2,2,1,"","AzureLogFormatter"],[2,1,1,"","LOGGING"],[2,6,1,"","set_root_loglevel"]],"codesign.util.logging.AzureLogFormatter":[[2,5,1,"","DEBUG_PREFIX"],[2,5,1,"","ERROR_PREFIX"],[2,5,1,"","WARNING_PREFIX"],[2,3,1,"","check_emit"],[2,3,1,"","format"],[2,3,1,"","group_end"],[2,3,1,"","group_start"],[2,3,1,"","section_start"]],"codesign.util.processes":[[2,6,1,"","popen_simple"],[2,6,1,"","run_subprocess"]],"tests.core":[[5,0,0,"-","test_codesign"],[5,0,0,"-","test_codesign_config"]],"tests.core.test_codesign":[[5,2,1,"","TestCodesign"]],"tests.core.test_codesign.TestCodesign":[[5,3,1,"","assertHasValidSigning"],[5,3,1,"","assertIsUnsigned"],[5,3,1,"","setUp"],[5,3,1,"","setUpClass"],[5,3,1,"","tearDown"],[5,3,1,"","test_lowercase_executable_name__setsBundleNameToLowercaseInPlistFile"],[5,3,1,"","test_pre_cleanup__removesSignaturesAsExpected"],[5,3,1,"","test_remove_component_plugins__shouldRemoveAllPluginFoldersOneLevelBelowEachComponent"],[5,3,1,"","test_remove_php__removesPhpDirectoryForMacIfPresent"],[5,3,1,"","test_remove_temp_files__deletesAllSpecifiedFilesRecursively"],[5,3,1,"","test_run__succeedsIfEnvironmentHasValidSetup"],[5,3,1,"","test_sign_app__succeedsIfEnvironmentHasValidSetup"],[5,3,1,"","test_sign_bin_dir__succeedsIfEnvironmentHasValidSetup"],[5,3,1,"","test_sign_components__succeedsIfEnvironmentHasValidSetup"],[5,3,1,"","test_sign_contents__succeedsIfEnvironmentHasValidSetup"],[5,3,1,"","test_sign_database__succeedsIfEnvironmentHasValidSetup"],[5,3,1,"","test_sign_frameworks__succeedsIfEnvironmentHasValidSetup"],[5,3,1,"","test_sign_helpers__succeedsIfEnvironmentHasValidSetup"],[5,3,1,"","test_sign_internal_components__succeedsIfEnvironmentHasValidSetup"],[5,3,1,"","test_sign_mecab__succeedsIfEnvironmentHasValidSetup"],[5,3,1,"","test_sign_native_components__succeedsIfEnvironmentHasValidSetup"],[5,3,1,"","test_sign_php__succeedsIfEnvironmentHasValidSetup"],[5,3,1,"","test_sign_plugins__succeedsIfEnvironmentHasValidSetup"],[5,3,1,"","test_sign_sasl_plugins__succeedsIfEnvironmentHasValidSetup"],[5,3,1,"","test_sign_updater__succeedsIfEnvironmentHasValidSetup"],[5,3,1,"","test_update_info_plist__updatesElementsAsExpected"]],"tests.core.test_codesign_config":[[5,2,1,"","TestCodesignConfig"]],"tests.core.test_codesign_config.TestCodesignConfig":[[5,3,1,"","setUp"],[5,3,1,"","setUpClass"],[5,3,1,"","tearDown"],[5,3,1,"","test_find_signing_identity__returnsFirstFoundIdentityIfCertificateIsInstalled"],[5,3,1,"","test_find_signing_identity__returnsNoneIfCertificateDoesNotExist"],[5,3,1,"","test_validate__raisesIfGivenBundleHasWrongSuffix"],[5,3,1,"","test_validate__raisesIfGivenBundleIsFile"],[5,3,1,"","test_validate__raisesIfGivenBundleNotExists"],[5,3,1,"","test_validate__raisesOnSigningIdentityMismatch"]],"tests.testhelper":[[4,1,1,"","DEVELOPER_ID_APPLICATION_ENTRY"],[4,1,1,"","MESSAGE_SKIPPED_CAUSED_BY_TEMPLATE"],[4,1,1,"","PATH_TO_4D_TEMPLATE_APP"],[4,1,1,"","PATH_TO_FIXTURE_DIR"],[4,1,1,"","PATH_TO_TEMP_DIR"],[4,1,1,"","PATH_TO_TEST_RESOURCES"],[4,6,1,"","create_app_template_file_copy"],[4,6,1,"","create_temp_testing_dir"],[4,6,1,"","remove_signing"]],"tests.util":[[6,0,0,"-","test_codesigning"],[6,0,0,"-","test_processes"]],"tests.util.test_codesigning":[[6,2,1,"","TestCodesigning"]],"tests.util.test_codesigning.TestCodesigning":[[6,3,1,"","assertHasValidSigning"],[6,3,1,"","setUp"],[6,3,1,"","setUpClass"],[6,3,1,"","tearDown"],[6,3,1,"","test_create_entitlements_plist_createsFileAsExpectedWithDefaultEntitlements"],[6,3,1,"","test_remove_extended_attributes__recursivelyRemovesAllExtendedAttributes"],[6,3,1,"","test_run_codesign_command__raisesWithStderrIfSomethingWentWrong"],[6,3,1,"","test_run_codesign_command__signsAsExpectedIfPassedValidArguments"],[6,3,1,"","test_run_install_name_tool__raisesIfFileOrDirectoryNotExists"],[6,3,1,"","test_run_install_name_tool__succeedsIfGivenPathsAndFrameworksExist"]],"tests.util.test_processes":[[6,2,1,"","TestProcesses"]],"tests.util.test_processes.TestProcesses":[[6,3,1,"","setUpClass"],[6,3,1,"","test_popen_simple__logsOutputAsExpectedIfValidCommandIsPassed"],[6,3,1,"","test_popen_simple__raisesOnCommandLineErrorAndIncludesStderrInMessage"],[6,3,1,"","test_run_subprocess__raisesOnCommandLineErrorAndIncludesStderrInMessage"],[6,3,1,"","test_run_subprocess__runsAsExpectedIfValidCommandIsPassed"]],codesign:[[1,0,0,"-","core"],[0,0,0,"-","main"],[2,0,0,"-","util"]],tests:[[5,0,0,"-","core"],[4,0,0,"-","testhelper"],[6,0,0,"-","util"]]},objnames:{"0":["py","module","Python module"],"1":["py","data","Python data"],"2":["py","class","Python class"],"3":["py","method","Python method"],"4":["py","property","Python property"],"5":["py","attribute","Python attribute"],"6":["py","function","Python function"]},objtypes:{"0":"py:module","1":"py:data","2":"py:class","3":"py:method","4":"py:property","5":"py:attribute","6":"py:function"},terms:{"0":2,"1":[0,2],"1ab1234567":1,"1xy2345678":4,"2":0,"2nd":0,"4d":[0,1,4],"4dcodesign":[0,4],"case":[5,6],"class":[1,2,5,6],"default":[0,1,2],"do":4,"final":[1,2,4],"function":[1,2],"import":2,"new":[2,4],"public":1,"return":[1,2,4],"static":[1,2],"true":[1,2],"while":1,A:2,At:1,If:2,In:1,The:[1,2],These:1,To:[0,4],Will:2,__name__:2,_from:2,_to:2,abort:1,about:1,action:1,activ:1,actual:1,ad:1,add:2,addit:[1,2],addition:2,after:[1,2,5,6],ag:4,aka:[1,2],all:[1,4],also:[1,2],although:1,alwai:1,an:[1,2,5],ani:4,app:[0,1,4],appar:1,append:2,appl:[1,2],appli:1,applic:[0,1,4],ar:[0,1,2],arg:2,argument:2,arm64:1,assert:[5,6],asserthasvalidsign:[5,6],assertisunsign:5,asynchron:2,attribut:2,automat:1,avoid:2,azur:[1,2],azurelogformatt:2,back:2,base:[1,2,5,6],becaus:1,been:1,befor:[1,2,4,5,6],being:2,below:1,bin:1,binari:2,bool:1,bottom:1,buggi:1,build:1,built:1,bundl:[1,2,4,5,6],bundleresourc:1,call:[1,2,4,5,6],callabl:2,caller:2,can:[0,1,2,5,6],cannot:1,carri:2,caus:1,cd:[0,4],certif:[1,2],chang:[0,1,2],check:2,check_emit:2,cheer:0,classmethod:[5,6],client:1,code:[0,1,2],codesign:[3,4,5,6],codesign_config:0,codesignconfig:[1,5],com:[1,2],command:[0,2,4],common:[1,2],complet:[1,2],completedprocess:2,compon:1,comput:2,concaten:2,config:1,configur:1,connect:1,constant:4,constraint:[1,2],contain:2,convert:2,convert_to_plist_format:2,copi:4,core:[0,4],correctli:1,coupl:2,crazi:1,creat:[1,2,4],create_app_template_file_copi:4,create_entitlements_plist:2,create_temp_testing_dir:4,current:1,custom:[1,2],custom_kei:1,data:[1,4],databas:1,datefmt:2,debug:[0,2],debug_prefix:2,deconstruct:[5,6],decor:2,dedic:[1,2],deep:[1,2],deepli:4,default_hardened_runtime_entitl:[0,1],default_info_plist_properti:[0,1],defin:[1,2],delet:1,determin:2,develop:[1,4],developer_id_application_entri:4,devop:2,dict:[1,2],dictionari:[1,2],differ:[1,2],dir:2,directori:[1,2,4],disabl:1,discov:4,doc:2,doctyp:2,document:1,doe:4,driven:4,dylib:1,dynam:2,e:1,each:1,els:1,emit:2,emitt:2,empti:4,en:2,enabl:1,enclos:2,entitl:[1,2],entri:[0,1],environ:1,equal:2,error:[0,2],error_prefix:2,establish:1,etc:[1,2],event:2,everyth:1,everywher:2,exactli:1,exampl:[1,2,4],except:[1,2],execut:[1,2],exercis:[5,6],exist:[1,2,4],exit:2,expect:2,extend:2,extens:1,extern:[0,1],f:1,fail:[2,4],fall:2,fals:1,fantast:4,fatal:[0,2],feel:1,file:[1,2,4,5,6],filenam:4,filter:[1,2],find:1,find_signing_ident:1,first:1,fix:1,fixtur:[4,5,6],fmt:2,forc:[1,2],format:2,formatexcept:2,formatt:2,formattim:2,found:1,framework:1,free:1,frequent:[2,4],from:[0,1,2],g:1,gener:4,get:2,getlogg:2,getmessag:2,given:[1,2],glow:1,go:2,goe:1,granular:1,group_end:2,group_start:2,ha:1,handl:1,handler:1,harden:[1,2],hardened_runtim:1,hardened_runtime_entitl:1,have:[0,1],helper:4,helpertool:1,here:1,hold:2,hook:[5,6],howev:1,html:1,http:[1,2],human:2,id:[1,4],ident:[1,2,4],implement:1,index:3,indirect:2,info:[0,1,2],inform:2,information_property_list:1,init:2,insert:1,instal:[1,2],install_name_tool:2,installtool:1,instanc:2,instead:2,integr:4,intern:1,invalid:1,is_linux:1,is_maco:1,is_running_azure_pipelin:1,is_window:1,issu:1,item:[1,2,5],item_to_sign:1,its:[1,2,4],js:1,json:1,just:2,keep:4,kei:1,keisuk:1,keychain:[1,4],kwarg:2,languag:1,larg:4,later:1,launch:1,launchservic:1,level:[0,1,2],lib4d:1,lib:1,libdigestmd5:1,librari:[1,2],line:[0,4],linux:1,list:[1,2],live:2,local:[1,5,6],locat:[1,2],log:0,logger:2,logrecord:2,look:[0,1],lowercas:1,lowercase_executable_nam:1,m:4,mach:2,maco:[1,4],mai:[1,4],main:[1,2,3],mainli:1,man:2,manifest:1,mayb:1,mecab:1,messag:[2,4],message_skipped_caused_by_templ:4,method:[5,6],methodnam:[5,6],microsoft:2,miyako:1,mobil:1,modifi:[1,4],modul:3,moment:1,more:2,most:1,move:1,must:[1,2],my4d:1,name:[1,2],narrow:1,nativ:1,necessari:1,need:1,nest:1,none:[1,2,5,6],normal:1,notar:1,note:[1,2],notset:2,o:2,objc:1,object:[1,2,4],of_typ:1,old:2,one:[1,4],oper:2,operand:2,option:[0,1,2],order:1,organ:1,origin:[1,2],os:1,osx:2,other:[1,2],otherwis:4,our:[1,4],out:[1,2],output:2,packag:3,page:[2,3],paramet:[0,1,2,4,5,6],parent:2,parser:2,pass:[0,1],path:[0,1,2,4,5,6],path_to_4d_template_app:4,path_to_app_bundl:[1,2],path_to_fixture_dir:4,path_to_item:[2,4,5,6],path_to_plist:[1,2],path_to_temp_dir:4,path_to_test_resourc:4,pathlib:[1,2,4,5,6],person:0,php:1,pipelin:[1,2],plist:[1,2],plist_data:1,plugin:1,point:[0,1],popen:2,popen_simpl:2,port:1,possibl:[0,1],pre_cleanup:1,preparatori:2,presum:1,print:2,problem:1,process:[0,1,6],processor:1,product:4,program:1,project:[0,4],properti:[0,1,2],provid:4,pure:2,py:[0,4],python:[0,1,2,4],qualifi:1,r4:1,r:2,rais:2,re:[1,2],readabl:2,recommend:1,record:2,recurs:[1,2],referenc:2,relat:4,remov:[1,2,4],remove_component_plugin:1,remove_extended_attribut:2,remove_php:1,remove_sign:4,remove_temp_fil:1,renam:4,replac:4,reportcrash:1,resign:1,resolv:2,resourc:4,respons:2,result:2,returncod:2,root:[0,2,4],run:[0,1,2,4,5,6],run_codesign_command:2,run_codesign_command_for_hardened_runtim:2,run_install_name_tool:2,run_remove_codesign_command:2,run_subprocess:2,runner_opt:[0,1],runtest:[5,6],runtim:[1,2],s:[1,2,4],save:4,script:2,search:[1,3],section_start:2,secur:1,see:[1,2],seem:1,self:[1,2],sequenc:1,server:1,set:[1,2,5,6],set_root_loglevel:2,setup:[5,6],setupclass:[5,6],sever:4,share:2,should:[1,2,4,5,6],show:1,sign:[0,1,2,4],sign_app:1,sign_bin_dir:1,sign_compon:1,sign_cont:1,sign_databas:1,sign_framework:1,sign_help:1,sign_internal_compon:1,sign_mecab:1,sign_mobil:1,sign_native_compon:1,sign_php:1,sign_plugin:1,sign_sasl_plugin:1,sign_updat:1,signatur:[1,2,4,5,6],signing_ident:1,simpl:2,simpli:[0,2,4],skip:4,softwar:4,some:1,sourc:[2,5,6],specifi:2,standalon:1,standard:2,stderr:2,stdin:2,stdout:2,step:2,still:1,store:4,str:[1,2,4],string:[2,4],stub:4,stuff:1,subcommand:2,subject:2,submodul:3,subpackag:3,subprocess:2,subprocesserror:2,suffici:1,suffix:1,t:[2,4],teardown:[5,6],temp:[2,4],temporari:[1,2,4],temporarydirectori:2,test:3,test_codesign:4,test_codesign_config:5,test_codesign_config_config:4,test_create_entitlements_plist_createsfileasexpectedwithdefaultentitl:6,test_find_signing_identity__returnsfirstfoundidentityifcertificateisinstal:5,test_find_signing_identity__returnsnoneifcertificatedoesnotexist:5,test_lowercase_executable_name__setsbundlenametolowercaseinplistfil:5,test_popen_simple__logsoutputasexpectedifvalidcommandispass:6,test_popen_simple__raisesoncommandlineerrorandincludesstderrinmessag:6,test_pre_cleanup__removessignaturesasexpect:5,test_process:4,test_remove_component_plugins__shouldremoveallpluginfoldersonelevelbeloweachcompon:5,test_remove_extended_attributes__recursivelyremovesallextendedattribut:6,test_remove_php__removesphpdirectoryformacifpres:5,test_remove_temp_files__deletesallspecifiedfilesrecurs:5,test_run__succeedsifenvironmenthasvalidsetup:5,test_run_codesign_command__raiseswithstderrifsomethingwentwrong:6,test_run_codesign_command__signsasexpectedifpassedvalidargu:6,test_run_install_name_tool__raisesiffileordirectorynotexist:6,test_run_install_name_tool__succeedsifgivenpathsandframeworksexist:6,test_run_subprocess__raisesoncommandlineerrorandincludesstderrinmessag:6,test_run_subprocess__runsasexpectedifvalidcommandispass:6,test_sign_app__succeedsifenvironmenthasvalidsetup:5,test_sign_bin_dir__succeedsifenvironmenthasvalidsetup:5,test_sign_components__succeedsifenvironmenthasvalidsetup:5,test_sign_contents__succeedsifenvironmenthasvalidsetup:5,test_sign_database__succeedsifenvironmenthasvalidsetup:5,test_sign_frameworks__succeedsifenvironmenthasvalidsetup:5,test_sign_helpers__succeedsifenvironmenthasvalidsetup:5,test_sign_internal_components__succeedsifenvironmenthasvalidsetup:5,test_sign_mecab__succeedsifenvironmenthasvalidsetup:5,test_sign_native_components__succeedsifenvironmenthasvalidsetup:5,test_sign_php__succeedsifenvironmenthasvalidsetup:5,test_sign_plugins__succeedsifenvironmenthasvalidsetup:5,test_sign_sasl_plugins__succeedsifenvironmenthasvalidsetup:5,test_sign_updater__succeedsifenvironmenthasvalidsetup:5,test_update_info_plist__updateselementsasexpect:5,test_validate__raisesifgivenbundlehaswrongsuffix:5,test_validate__raisesifgivenbundleisfil:5,test_validate__raisesifgivenbundlenotexist:5,test_validate__raisesonsigningidentitymismatch:5,testcas:[5,6],testcodesign:[5,6],testcodesignconfig:5,testhelp:3,testprocess:6,text:2,thei:1,them:1,therefor:1,thi:[0,1,2,4],thing:1,thu:4,time:2,top:[1,2],trim:0,two:1,type:1,under:1,unfortun:1,unit:[4,5],unittest:[4,5,6],unix:2,unsign:5,up:[1,5,6],updat:1,update_info_plist:1,us:[1,2,4],usagedescript:1,user:1,usestim:2,util:[0,4],v19:1,v:4,valid:[1,5,6],valu:[0,2],variabl:1,ve:1,verifi:[5,6],version:4,via:4,view:2,wa:[1,2],warn:[0,2,4],warning_prefix:2,we:1,websit:1,webviewercef:1,when:2,which:[1,2],whose:[1,4,5,6],window:1,within:[1,2],work:4,wrapper:2,write:2,written:2,www:2,xattr:2,xml:2,xy:1,yet:1,yield:2,you:0,your:[0,1,4],zsh:4},titles:["codesign package","codesign.core package","codesign.util package","Welcome to 4DCodesign\u2019s documentation!","tests package","tests.core package","tests.util package"],titleterms:{"4dcodesign":3,codesign:[0,1,2],codesign_config:1,content:[0,1,2,3,4,5,6],core:[1,5],document:3,indic:3,log:2,main:0,modul:[0,1,2,4,5,6],packag:[0,1,2,4,5,6],process:2,s:3,submodul:[0,1,2,4,5,6],subpackag:[0,4],tabl:3,test:[4,5,6],test_codesign:[5,6],test_codesign_config_config:5,test_process:6,testhelp:4,util:[2,6],welcom:3}})