# was_configureRole Name: was_configure


**was_configure** - роль взаимодействия с IBM WebSphere Application Serve.  Ключевой особенностью роли является автогенерация скриптов с необходимыми действиями для WAS по шаблонам.

- Работа с кластерами и standelone серверами
- Установка, удаление, обновление, переустановка приложений
- Конфигурация приложений
- Остановка, запуск Activation specifications через wsadmin
- Остановка, запуск приложений через wsadmin
- Перезапуск standelone серверов через wsadmin
- Остановка, запуск кластеров через wsadmin
- Легкое увеличение функционала через простое добавление шаблонов



Requirements:
---------

-  Ansible >= ansible 2.4.0.0
-  WebSphere Application Server >= 8.5.5.9 *(на других версиях не проверялось)*

**[Libs]**

-  OABS_wsadminlib.py  (Jython lib Библиотека взаимодействия) 


**[windows]**

-  PowerShell v3.0 и выше
-  служба WinRM должна быть запущенна

Dependencies
---------
**[Ansible modules]**

-  win_wsadmin.ps1 (Ansible lib модуль упрощенной работы с wsadmin [windows])
-  wsadmin.py	(Ansible lib модуль упрощенной работы с wsadmin [Nix*])
  
**[Ansible facts]**

- ansible_os_family
- ansible_date_time
> **Если Ansible facts не доступны требуется добавить следующий код:**
> 
>		ansible_date_time:
>		  date: "{{ lookup('pipe', 'date +%Y-%m-%d') }}"
>		  time: "{{ lookup('pipe', 'date +%H:%M:%S') }}"
>		
>		[для Windows]
>		ansible_os_family: 'Windows'
>		[для Nix]
>		ansible_os_family: 'Nix'

Role Variables
---------
## Обязательные параметры: ##

- **`was_home:`** Директория инсталляции IBM WAS;
> 
>		[Windows]: 
>	         was_home: D:/IBM/WebSphere8/AppServer
>		[Nix]:     
>	         was_home: /u01/IBM/WebSphere/AppServer

- **`was_temp_dir:`** Временная рабочая директория;
	
>  ! Важно если последней директории нет задание ее создаст, но если нет и промежуточной будет ошибка!;
>  
>		[для Windows]: 
>		    was_temp_dir: D:/temp/ansible_work
>		[для Nix]: 
>		    was_temp_dir: /tmp/ansible_work

- **`was_applications:`** Массив описания приложения(й);

>		was_applications:
>		  app_name: #Имя приложения в WAS# test_app     
>		  mask: #Маска поиска приложения (статичная часть имени приложения)# test_
>		  clu_name: #Имя кластера(ов) для работы. Если нет кластера не указывать!#
>		    - IFT1 
>		  parameters: #Опциональная секция (массив) параметров для работы с приложением#
>		    notCriticalAS:
>		      - ru.sbt.storage.reports.message.ReportProcessMQActivation
>		      - ru.sbt.storage.reports.message.SlowReportProcessMQActivation
>		      - ru.sbrf.gamma.storage.mdb.FilialBagMQActivatio
>		    contextroot: #Контекст роот для приложения# '/test'
>		    usedefaultbindings: 'True'
    
- **`steps:`** Массив шаблонв для генератора скриптов (элементы массива представлены в виде пар ключ/значение, где ключ всегда script, а значение имя шаблона без расширения). По умолчанию если не задано: 
>    steps: { script: "debug" }

- **`was_script:`** Алиас для скриптов, логов;
- **`copy_file:`** Данный параметр отвечает за поиск и копирование файлов (приложений) на целевой хост, а также конфигурацию итогового скрипта может принимать два значения: true/false

## Не обязательные параметры: ##
- 	**`log_level:`** Уровень логирования 0 - минимум 3 - максимум. По умолчанию если не задано 1;
-   **`was_username:`** имя пользователя для подключения. По умолчанию если не задано ""( не используется);
-   **`was_password:`** пароль пользователя для подключения. По умолчанию если не задано ""( не используется);
-   **`profile_name:`** Имя профайла для работы. По умолчанию если не задано ""( не используется, тогда требуется указать параметры wsadminHost и wsadminPort);
>		    profile_name: dmgr
>		    или: 
>		    profile_name: appsrv01
-   **`profile_home:`** Путь до профайла (`'{{ was_home }}\profiles\{{ profile_name }}'`);
-   **`wsadminHost:`** Хост для подключений. По умолчанию если не задано ""( не используется);
-   **`wsadminPort:` **Порт для подключения. По умолчанию если не задано ""( не используется);
-   **`wsadminConttype:`** Тип подключения По умолчанию если не задано "SOAP";
-   **`wsadminLang:`** Язык скриптов для выполнения (по умолчанию `jython`);
-   **`wsadminXmx:`** число (аналог`javaoption -Xmx2048m`) По умолчанию если не задано ""( не используется);
-   **`wsadminXms:`** число (аналог`javaoption -Xms512m`) По умолчанию если не задано ""( не используется);
-   **`wsadminTimeOut:`** число (аналог`javaoption -Dcom.ibm.SOAP.requestTimeout=540`) По умолчанию если не задано ""( не используется);
-   **`wsadminScriptParam:`** Параметры запуска скрипта при использовании генератора шаблонов не используются;
-   **`wsadminAcceptCert:`**  Разрешение на принятие сертификата WAS при использовании wsadmin из папки профайла и без указания хоста не используется (`false/true`)По умолчанию если не задано "false"( не используется); 


Алгоритм работы:
---------
>
1. Роль считывает входящие параметры (список необходимых действий из конфигурации) и генерирует шаблон исполняемого скрипта на целевом хосте
2. Определяет тип используемой ОС хоста(ов)
3. В рабочей директории создается временный каталог (если отсутствует)
4. Проверяется наличие устаревших файлов и их удаление
5. Копирование рабочей библиотеки (OABS_wsadminlib.py) во временный каталог
6. Определяется список приложений для работы
7. Копирование приложения(й) во временный каталог
8. Рендеринг (заполнение входящими данными) шаблона исполняемого скрипта и его перенос на целевой хост
9. Запуск wsadmin и передача скрипта на выполнение
10. Сбор и архивация лог фалов 
11. Очистка временной директории


Example конфигурация роли:
=========

>             #Параметры подключения
>             profile_name: autotest1
>             was_temp_dir: D:/musor/ansible_work
>             was_home: D:/IBM/WebSphere/AppServer
>             profile_home: '{{ was_home }}/profiles/{{ profile_name }}'
>             was_password: SuperPassword
>             was_username: admin
>             wsadminXmx: 2048
>             wsadminTimeOut: 540
>             #Параметры приложений
>             was_applications:
>               - app_name: test_app1
>                 mask: test-1
>                 parameters:
>                   contextroot: /mis
>                    usedefaultbindings: True
>               - app_name: SUDIR
>                 mask: sudir-ear



Example Конфигурация генератора скриптов из шаблонов (Jython) для WAS
---------

>             #Наборы шаблонов для данной роли из конфигурации
>             step_deploy:
>               - script: stop_app
>               - script: stop_cluster
>               - script: reinstall_app
>               - script: start_cluster
>               - script: start_app

Представляет собой массив с пошаговым перечнем необходимых шагов.
Данные шаги подразделяются на два условных типа:

-  Независящие шаги
-  Зависящие шаги

Основное отличие в том, что не все шаги можно выполнять в произвольном порядке, но к примеру их можно выполнять как отдельную задачу или в конце скрипта.

Общий вид массива:

    some_step:
      - { script: "some_actions1"}
      - { script: "some_actions2"}

some_step - имя массива передаваемое роли
some_actions - имя шаблона без разрешения


>		------------------------------|-------------|--------------------------------------------------------------------------------
>		| Имя шаблона                 | Независящий?|Описание                                                                       |
>		|-----------------------------|-------------|-------------------------------------------------------------------------------|
>		|start.j2                     |НЕТ          |Импортируется всегда сам указания не требует необходим для работы всех шаблонов|
>		|-----------------------------|-------------|-------------------------------------------------------------------------------|		
>		|delete_app.j2                |ДА           |Удаление приложения(й) если существует                                         |
>		|-----------------------------|-------------|-------------------------------------------------------------------------------|		
>		|install_app.j2               |ДА           |Установка приложения(й)                                                        |
>		|-----------------------------|-------------|-------------------------------------------------------------------------------|		
>		|update_app.j2                |ДА           |Обновление приложения(й) если существует                                       |
>		|-----------------------------|-------------|-------------------------------------------------------------------------------|
>		|reinstall_app.j2             |ДА           |Переустановка приложения(й)                                                    |
>		|-----------------------------|-------------|-------------------------------------------------------------------------------|	
>		|stop_app.j2                  |ДА           |Остановка приложения(й)                                                        |
>		|-----------------------------|-------------|-------------------------------------------------------------------------------|	
>		|start_app.j2                 |ДА           |Запуск приложения(й)                                                           |
>		|-----------------------------|-------------|-------------------------------------------------------------------------------|
>		|stop_activ_spec.j2           |ДА           |Остановка ActivationSpec                                                       |
>		|-----------------------------|-------------|-------------------------------------------------------------------------------|
>		|debug.j2                     |НЕТ          |Вывод диагностической информации НЕ вносит изменений проверяет правильность    |
>		|                             |             |конфигурации                                                                   |
>		|-----------------------------|-------------|-------------------------------------------------------------------------------|		
>		|restart_was_server.j2        |НЕТ          |Перезапуск сервера WAS БЕЗ КЛАСТЕРА                                            |
>		|-----------------------------|-------------|-------------------------------------------------------------------------------|		
>		|start_all_cluster_servers.j2 |НЕТ          |Запуск всех кластеров приложений                                               |
>		|-----------------------------|-------------|-------------------------------------------------------------------------------|		
>		|start_cluster.j2             |НЕТ          |Запуск кластеров указанных в конфигурации                                      |
>		|-----------------------------|-------------|-------------------------------------------------------------------------------|		
>		|stop_all_cluster_servers.j2  |НЕТ          |Остановка всех кластеров приложений                                            |
>		|-----------------------------|-------------|-------------------------------------------------------------------------------|		
>		|stop_cluster.j2              |НЕТ          |Остановка кластеров указанных в конфигурации                                   |
>		------------------------------|-------------|--------------------------------------------------------------------------------


  

Пример ansible-playbook:
---------
## Использование как роли: ##
    ---
    - hosts: **some_host**
      vars:
        # Определяем рабочую директорию относительно плейбука
        # playbook_dir переменная от ansible
        work_dir: "{{ playbook_dir }}"
      tasks:
      - name: Обращение к роли was_configure
        import_role:
          # Имя импортируемой роли (директории роли в директории roles)
          name: was_configure
        vars:
          #Наборы шаблонов для данной роли
          steps:
            - script: stop_app
            - script: stop_cluster
            - script: reinstall_app
            - script: start_cluster
            - script: start_app
          #Алиас для скриптов, логов, ...
          was_script: 'deploy_apps'
          #Данный параметр отвечает за поиск и копирование файлов (приложений) на целевой хост, а также конфигурацию итогового скрипта может принимать два значения:
          #  False - Поиск и копирование отключены скрипт получает минимум данных (все что описано в свойствах хоста)
          #  True - Поиск и копирование разрешены произойдет поиск приложений описанных в свойствах хоста эта информация передастся итоговому скрипту после копирования файлов.
          copy_file: true
    ...


Author Information
---------
Румянцев Юрий Николаевич
[rumyanec@gmail.com](mailto:"rumyanec@gmail.com")
