
## roles 的搜索路径


• Ansible 在遇到：

  roles:
    - install_nginx

  或：

  - ansible.builtin.include_role:
      name: install_nginx

  时，会在一系列目录中查找名为 install_nginx 的目录。常见搜索顺序可以理解为：

  1. 当前 Playbook 所在目录下的 roles/
  2. Ansible 配置文件 ansible.cfg 中的 roles_path
  3. ~/.ansible/roles/
  4. /usr/share/ansible/roles/
  5. /etc/ansible/roles/

  例如项目结构：

  project/
  ├── playbooks/
  │   └── deploy.yml
  └── roles/
      └── install_nginx/
          └── tasks/main.yml

  如果 deploy.yml 在 playbooks/ 下，默认会优先找：

  project/playbooks/roles/install_nginx/

  这往往不是你实际存放 role 的位置。因此项目中通常会在仓库根目录放一个 ansible.cfg：

  [defaults]
  roles_path = ./roles

  但这里也有一个容易忽略的点：./roles 通常相对于执行 ansible-playbook 命令时的当前工作目录，而不是相对于 ansible.cfg 文件。因此，最稳妥的做法是从项目根目录执行：

  cd project
  ansible-playbook -i inventory playbooks/deploy.yml

  也可以使用环境变量临时指定：

  export ANSIBLE_ROLES_PATH="$PWD/roles"
  ansible-playbook -i inventory playbooks/deploy.yml

  多个 role 路径用冒号分隔（Linux/macOS）：

  [defaults]
  roles_path = ./roles:/opt/company/ansible-roles

  你可以用下面命令确认当前生效的路径：

  ansible-config dump --only-changed
  ansible-config dump | rg DEFAULT_ROLES_PATH

  它会显示类似：

  DEFAULT_ROLES_PATH(/path/to/ansible.cfg) = ['/项目路径/roles', ...]

  实际项目里我更推荐固定成这种结构：

  project/
  ├── ansible.cfg
  ├── inventory/
  ├── playbooks/
  └── roles/
      ├── install_nginx/
      └── deploy_app/

  并且始终在 project/ 根目录运行 Playbook。这样 role 的定位规则明确，也不会依赖个人机器上的 ~/.ansible/roles。

```
  roles/install_nginx/
  ├── defaults/main.yml             # 默认变量(可以被覆盖)
  ├── vars/main.yml                 # 内部变量(不可以被覆盖)
  ├── tasks/main.yml
  ├── handlers/main.yml
  ├── templates/nginx.conf.j2
  ├── files/
  └── meta/main.yml
```

```
  Playbook
    -> 加载 role 的 defaults / vars
    -> 处理 meta 中的依赖 role（若存在）
    -> 执行 tasks/main.yml
         -> 需要配置文件时，渲染 templates/nginx.conf.j2
         -> 需要静态文件时，读取 files/ 下的文件
         -> 任务变更时通知 handlers/main.yml
    -> 当前 play 结束时执行被通知的 handler
```

   文件/目录                                      是否自动读取    功能
  ━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   tasks/main.yml                                           是    role 的入口任务。例如安装 Nginx、创建配置目录、写入配置、启动服务。
  ─────────────────────────  ──────────────────────────────────  ────────────────────────────────────────────────────────────────────────────────────────
   defaults/main.yml                                        是    默认变量，优先级较低，方便调用 role 的 Playbook 覆盖。
  ─────────────────────────  ──────────────────────────────────  ────────────────────────────────────────────────────────────────────────────────────────
   vars/main.yml                                            是    role 内部固定变量，优先级高于 defaults，通常不希望外部随意改变。
  ─────────────────────────  ──────────────────────────────────  ────────────────────────────────────────────────────────────────────────────────────────
   handlers/main.yml              会加载定义，但仅被通知后执行    放置重启/重载 Nginx 这类动作，避免每个任务都重复重启服务。
  ─────────────────────────  ──────────────────────────────────  ────────────────────────────────────────────────────────────────────────────────────────
   templates/nginx.conf.j2    否，只有 template 任务引用时读取    Jinja2 模板。Ansible 用变量渲染后，生成目标机器上的 /etc/nginx/nginx.conf 等配置文件。
  ─────────────────────────  ──────────────────────────────────  ────────────────────────────────────────────────────────────────────────────────────────
   files/                       否，只有 copy 等任务引用时读取    存放无需变量替换的静态文件，如证书、静态 HTML、固定脚本。
  ─────────────────────────  ──────────────────────────────────  ────────────────────────────────────────────────────────────────────────────────────────
   meta/main.yml                                  有内容时读取    定义依赖 role，例如 Nginx 依赖某个基础环境 role。



› 使用的时候，可以只使用role  中的一个 task 么？


• 可以，但不能在 roles: 列表里直接写“执行第 3 个 task”。Role 的默认行为始终是执行 tasks/main.yml 中的全部任务。

  如果你想只执行 role 中某一组任务，通常有两种方式。

  第一种是把任务拆到独立文件，再用 tasks_from 指定加载哪个文件。这是更清晰、也更推荐的方式：

  roles/install_nginx/tasks/
  ├── main.yml
  ├── install.yml
  ├── configure.yml
  └── service.yml

  # playbook.yml
  - hosts: webservers
    become: true
    tasks:
      - name: 只部署 Nginx 配置
        ansible.builtin.include_role:
          name: install_nginx
          tasks_from: configure.yml

  这样只会执行 roles/install_nginx/tasks/configure.yml 中的任务，不会自动执行 tasks/main.yml、install.yml 或 service.yml。

  如果任务在执行前就确定，也可使用静态导入：

  - hosts: webservers
    tasks:
      - name: 只执行 Nginx 配置任务
        ansible.builtin.import_role:
          name: install_nginx
          tasks_from: configure.yml

  第二种是使用 tags。给 role 中的 task 标记标签：

  # roles/install_nginx/tasks/main.yml
  - name: 安装 Nginx
    ansible.builtin.package:
      name: nginx
      state: present
    tags: [install]

  - name: 部署 Nginx 配置
    ansible.builtin.template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    tags: [configure]
    notify: Reload nginx

  - name: 启动 Nginx
    ansible.builtin.service:
      name: nginx
      state: started
    tags: [service]

  执行时筛选：

  ansible-playbook -i inventory playbook.yml --tags configure

  这会只执行带 configure 标签的任务。

  实际工程中建议这样选择：

  - 需要把“安装 / 配置 / 服务管理”等能力独立复用：拆分 install.yml、configure.yml，通过 tasks_from 调用。
  - 只是临时跳过或筛选某些步骤：使用 tags。
  - 不建议依赖 task 在 main.yml 中的顺序或名称来“只执行其中一个”，因为 role 一旦调整，调用方就会变得脆弱。


› 给我解释一下 nigix 这个role 在执行的时候，分别会去读哪些 文件，以及这些文件的功能

• 以之前的 roles/install_nginx 为例，执行下面的 Playbook 时：

  - hosts: webservers
    become: true
    roles:
      - install_nginx

  Ansible 会先定位 role 目录，再按约定加载或按任务引用相应文件。并不是 role 下的所有文件都会无条件执行。

  roles/install_nginx/
  ├── defaults/main.yml
  ├── vars/main.yml
  ├── tasks/main.yml
  ├── handlers/main.yml
  ├── templates/nginx.conf.j2
  ├── files/
  └── meta/main.yml

  执行过程可以理解为：

  Playbook
    -> 加载 role 的 defaults / vars
    -> 处理 meta 中的依赖 role（若存在）
    -> 执行 tasks/main.yml
         -> 需要配置文件时，渲染 templates/nginx.conf.j2
         -> 需要静态文件时，读取 files/ 下的文件
         -> 任务变更时通知 handlers/main.yml
    -> 当前 play 结束时执行被通知的 handler

  各文件的作用如下：

   文件/目录                                      是否自动读取    功能
  ━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   tasks/main.yml                                           是    role 的入口任务。例如安装 Nginx、创建配置目录、写入配置、启动服务。
  ─────────────────────────  ──────────────────────────────────  ────────────────────────────────────────────────────────────────────────────────────────
   defaults/main.yml                                        是    默认变量，优先级较低，方便调用 role 的 Playbook 覆盖。
  ─────────────────────────  ──────────────────────────────────  ────────────────────────────────────────────────────────────────────────────────────────
   vars/main.yml                                            是    role 内部固定变量，优先级高于 defaults，通常不希望外部随意改变。
  ─────────────────────────  ──────────────────────────────────  ────────────────────────────────────────────────────────────────────────────────────────
   handlers/main.yml              会加载定义，但仅被通知后执行    放置重启/重载 Nginx 这类动作，避免每个任务都重复重启服务。
  ─────────────────────────  ──────────────────────────────────  ────────────────────────────────────────────────────────────────────────────────────────
   templates/nginx.conf.j2    否，只有 template 任务引用时读取    Jinja2 模板。Ansible 用变量渲染后，生成目标机器上的 /etc/nginx/nginx.conf 等配置文件。
  ─────────────────────────  ──────────────────────────────────  ────────────────────────────────────────────────────────────────────────────────────────
   files/                       否，只有 copy 等任务引用时读取    存放无需变量替换的静态文件，如证书、静态 HTML、固定脚本。
  ─────────────────────────  ──────────────────────────────────  ────────────────────────────────────────────────────────────────────────────────────────
   meta/main.yml                                  有内容时读取    定义依赖 role，例如 Nginx 依赖某个基础环境 role。

  一个典型的 tasks/main.yml 可能是：

  - name: 安装 Nginx
    ansible.builtin.package:
      name: nginx
      state: present

  - name: 部署 Nginx 配置
    ansible.builtin.template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
      mode: "0644"
    notify: Reload nginx

  - name: 确保 Nginx 已启动
    ansible.builtin.service:
      name: nginx
      state: started
      enabled: true

  这里的重点是：

  1. 执行 template 任务时，Ansible 会自动到当前 role 的 templates/ 目录找 nginx.conf.j2。
  2. 模板中的 {{ nginx_port }}、{{ server_name }} 等变量，会优先从 Playbook、Inventory、vars/main.yml、defaults/main.yml 等变量来源解析。
  3. 若渲染后的目标文件确实发生变化，notify: Reload nginx 会标记 handler。
  4. 任务并不会立刻重载服务；通常在该 play 的任务执行完后，才运行：

  # handlers/main.yml
  - name: Reload nginx
    ansible.builtin.service:
      name: nginx
      state: reloaded

  例如默认变量放在 defaults/main.yml：

  nginx_listen_port: 80
  nginx_server_name: _

  调用时可以覆盖它：

  - hosts: webservers
    roles:
      - role: install_nginx
        vars:
          nginx_listen_port: 8080
          nginx_server_name: app.example.com

  最终模板得到的是 8080 和 app.example.com，而不是 role 默认值。

  一个容易混淆的点：templates/、files/、handlers/ 不是“放进去就自动执行”。真正的执行入口始终是 tasks/main.yml；它引用模板、复制静态文件或通知 handler 时，对应内容才会被使用。









› 给我介绍一下 role 的使用


• Role 是 Ansible 里最重要的复用机制，可以把一组任务、变量、模板、文件、handlers 等封装成一个“模块化组件”。

  你可以把 role 理解成：

  > 一个可复用的 playbook 组件。

  比如：

  - install_nginx：安装并启动 Nginx
  - install_jdk：安装 JDK
  - deploy_app：部署应用
  - init_database：初始化数据库
  - smoke_test：执行冒烟测试

  ———

  1. Role 的基本目录结构

  通常使用命令创建：

  ansible-galaxy init deploy_app

  生成结构大概是：

  deploy_app/
  ├── defaults/
  │   └── main.yml
  ├── files/
  ├── handlers/
  │   └── main.yml
  ├── meta/
  │   └── main.yml
  ├── tasks/
  │   └── main.yml
  ├── templates/
  ├── tests/
  │   ├── inventory
  │   └── test.yml
  └── vars/
      └── main.yml

  最常用的是这几个目录：

  tasks/       # 任务列表，role 的核心
  defaults/    # 默认变量，优先级低，适合放可覆盖配置
  vars/        # role 内部变量，优先级高，不建议乱用
  templates/   # Jinja2 模板文件
  files/       # 静态文件
  handlers/    # 被 notify 触发的动作，比如重启服务
  meta/        # role 元信息、依赖关系

  ———

  2. 一个简单 Role 示例

  假设我们写一个 install_nginx role。

  目录：

  roles/
  └── install_nginx/
      ├── tasks/
      │   └── main.yml
      ├── defaults/
      │   └── main.yml
      ├── handlers/
      │   └── main.yml
      └── templates/
          └── nginx.conf.j2

  roles/install_nginx/defaults/main.yml：

  nginx_port: 80
  nginx_worker_processes: auto

  roles/install_nginx/tasks/main.yml：

  - name: Install nginx
    ansible.builtin.yum:
      name: nginx
      state: present

  - name: Render nginx config
    ansible.builtin.template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    notify: Restart nginx

  - name: Ensure nginx is running
    ansible.builtin.service:
      name: nginx
      state: started
      enabled: true

  roles/install_nginx/handlers/main.yml：

  - name: Restart nginx
    ansible.builtin.service:
      name: nginx
      state: restarted

  roles/install_nginx/templates/nginx.conf.j2：

  worker_processes {{ nginx_worker_processes }};

  events {
      worker_connections 1024;
  }

  http {
      server {
          listen {{ nginx_port }};

          location / {
              return 200 "nginx is running\n";
          }
      }
  }

  ———

  3. 在 Playbook 中使用 Role

  主 playbook 可以这样写：

  - name: Install nginx on web servers
    hosts: web_servers
    become: true

    roles:
      - install_nginx

  执行：

  ansible-playbook -i inventory.ini site.yml

  Ansible 会自动去 roles/install_nginx/ 下面找：

  tasks/main.yml
  defaults/main.yml
  handlers/main.yml
  templates/
  files/

  ———

  4. 给 Role 传参数

  Role 的价值在于可配置、可复用。

  比如同一个 install_nginx role，在不同机器上监听不同端口：

  - name: Install nginx
    hosts: web_servers
    become: true

    roles:
      - role: install_nginx
        nginx_port: 8080
        nginx_worker_processes: 2

  这样会覆盖 defaults/main.yml 里的默认值。

  ———

  5. Role 变量的常见来源

  变量可以放在多个地方：

  roles/install_nginx/defaults/main.yml     # 默认值，优先级低
  roles/install_nginx/vars/main.yml         # role 内部变量，优先级高
  group_vars/web_servers.yml                # 主机组变量
  host_vars/server01.yml                    # 单台主机变量
  playbook 中 roles 传参                    # 显式传入变量
  命令行 -e                                 # 优先级很高

  例如：

  ansible-playbook -i inventory.ini site.yml -e "nginx_port=9090"

  一般建议：

  - 可配置项放 defaults/main.yml
  - 环境差异放 group_vars/
  - 不希望用户随便覆盖的内部变量才放 vars/main.yml

  ———

  6. Role 中使用 templates

  如果配置文件需要根据环境变化，就放到 templates/。

  任务：

  - name: Generate app config
    ansible.builtin.template:
      src: app.conf.j2
      dest: /opt/app/app.conf

  模板 templates/app.conf.j2：

  app.name={{ app_name }}
  app.port={{ app_port }}
  app.env={{ app_env }}
  db.host={{ db_host }}

  变量可以来自：

  app_name: order-service
  app_port: 8080
  app_env: test
  db_host: test-db.example.com

  ———

  7. Role 中使用 files

  files/ 目录用于放静态文件，不需要变量渲染。

  例如：

  roles/deploy_app/
  ├── files/
  │   └── app.jar
  └── tasks/
      └── main.yml

  任务：

  - name: Copy app package
    ansible.builtin.copy:
      src: app.jar
      dest: /opt/app/app.jar

  注意：

  - copy: src: app.jar 会自动从当前 role 的 files/ 目录找。
  - 如果文件需要变量替换，用 templates/。
  - 如果文件只是原样复制，用 files/。

  ———

  8. Role 中使用 handlers

  handlers 适合处理“配置变更后才执行”的动作，比如重启服务。

  任务：

  - name: Update nginx config
    ansible.builtin.template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    notify: Restart nginx

  handler：

  - name: Restart nginx
    ansible.builtin.service:
      name: nginx
      state: restarted

  只有当模板内容真的发生变化时，Restart nginx 才会执行。

  这也是 Ansible 幂等性的体现。

  ———

  9. Role 之间的依赖

  可以在 meta/main.yml 里声明依赖。

  比如 deploy_app 依赖 install_jdk：

  dependencies:
    - role: install_jdk

  这样执行 deploy_app 时，会先执行 install_jdk。

  不过实际项目中，我更建议在主 playbook 里显式排列 role：

  roles:
    - install_jdk
    - deploy_app
    - smoke_test

  这样流程更清晰。

  ———

  10. 使用 include_role 和 import_role

  除了在 roles: 里声明，也可以在 tasks 中调用 role。

  静态导入：

  - name: Import install_nginx role
    ansible.builtin.import_role:
      name: install_nginx

  动态导入：

  - name: Include install_nginx role
    ansible.builtin.include_role:
      name: install_nginx

  常见用法是配合条件：

  - name: Install nginx only on web nodes
    ansible.builtin.include_role:
      name: install_nginx
    when: "'web' in group_names"

  或者配合循环：

  - name: Deploy multiple services
    ansible.builtin.include_role:
      name: deploy_app
    loop:
      - order-service
      - user-service
      - payment-service
    loop_control:
      loop_var: service_name

  ———

  11. Role 和 tag 配合使用

  可以给 role 打 tag：

  - name: Deploy application
    hosts: app_servers
    become: true

    roles:
      - role: install_jdk
        tags:
          - jdk

      - role: deploy_app
        tags:
          - deploy

      - role: smoke_test
        tags:
          - smoke

  只执行部署：

  ansible-playbook -i inventory.ini site.yml --tags deploy

  只执行冒烟测试：

  ansible-playbook -i inventory.ini site.yml --tags smoke

  跳过冒烟测试：

  ansible-playbook -i inventory.ini site.yml --skip-tags smoke

  ———

  12. 自动化测试场景下的 Role 设计

  如果你是做自动化测试平台，可以这样拆：

  roles/
  ├── prepare_env/
  │   └── tasks/main.yml
  ├── install_dependencies/
  │   └── tasks/main.yml
  ├── deploy_service/
  │   └── tasks/main.yml
  ├── init_test_data/
  │   └── tasks/main.yml
  ├── run_api_test/
  │   └── tasks/main.yml
  ├── run_smoke_test/
  │   └── tasks/main.yml
  ├── collect_logs/
  │   └── tasks/main.yml
  └── cleanup_env/
      └── tasks/main.yml

  主流程：

  - name: Automated testing workflow
    hosts: test_servers
    become: true

    roles:
      - prepare_env
      - install_dependencies
      - deploy_service
      - init_test_data
      - run_smoke_test
      - collect_logs

  如果清理环境单独执行：

  ansible-playbook -i inventory.ini test.yml --tags cleanup

  ———

  13. 一个部署应用的 Role 示例

  目录：

  roles/
  └── deploy_app/
      ├── defaults/
      │   └── main.yml
      ├── tasks/
      │   └── main.yml
      ├── templates/
      │   └── app.service.j2
      └── handlers/
          └── main.yml

  defaults/main.yml：

  app_name: demo-service
  app_user: app
  app_dir: /opt/demo-service
  app_package: demo-service.jar
  app_port: 8080

  tasks/main.yml：

  - name: Create app user
    ansible.builtin.user:
      name: "{{ app_user }}"
      shell: /sbin/nologin
      create_home: false

  - name: Create app directory
    ansible.builtin.file:
      path: "{{ app_dir }}"
      state: directory
      owner: "{{ app_user }}"
      group: "{{ app_user }}"
      mode: "0755"

  - name: Copy app package
    ansible.builtin.copy:
      src: "{{ app_package }}"
      dest: "{{ app_dir }}/{{ app_name }}.jar"
      owner: "{{ app_user }}"
      group: "{{ app_user }}"
      mode: "0644"
    notify: Restart app

  - name: Render systemd service
    ansible.builtin.template:
      src: app.service.j2
      dest: "/etc/systemd/system/{{ app_name }}.service"
      mode: "0644"
    notify:
      - Reload systemd
      - Restart app

  - name: Ensure app is running
    ansible.builtin.systemd:
      name: "{{ app_name }}"
      state: started
      enabled: true

  handlers/main.yml：

  - name: Reload systemd
    ansible.builtin.systemd:
      daemon_reload: true

  - name: Restart app
    ansible.builtin.systemd:
      name: "{{ app_name }}"
      state: restarted

  templates/app.service.j2：

  [Unit]
  Description={{ app_name }}
  After=network.target

  [Service]
  User={{ app_user }}
  WorkingDirectory={{ app_dir }}
  ExecStart=/usr/bin/java -jar {{ app_dir }}/{{ app_name }}.jar --server.port={{ app_port }}
  Restart=always

  [Install]
  WantedBy=multi-user.target

  调用：

  - name: Deploy demo service
    hosts: app_servers
    become: true

    roles:
      - role: deploy_app
        app_name: order-service
        app_package: order-service.jar
        app_port: 8081

  ———

  14. Role 使用建议

  - 一个 role 只做一类事情，不要把部署、测试、清理都塞进一个 role。
  - 默认变量放 defaults/main.yml，方便外部覆盖。
  - 配置文件优先用 templates/，不要在任务里硬编码。
  - 服务重启放 handlers/，不要每次都强制重启。
  - 不同环境用 group_vars/ 管理变量。
  - role 名称尽量语义清晰，比如 install_jdk、deploy_app、smoke_test。
  - 复杂 role 可以拆多个任务文件，然后在 tasks/main.yml 里 import_tasks。

  例如：

  - import_tasks: install.yml
  - import_tasks: config.yml
  - import_tasks: service.yml
  - import_tasks: verify.yml

  一句话总结：

  Role 就是 Ansible 的“组件化机制”。
  Playbook 负责组织流程，Role 负责封装可复用能力，变量负责适配不同环境。




## 附录

› 这个工具playbook 如何复用呢?


• Ansible Playbook 的复用，核心思路是：不要把所有步骤都写在一个大 playbook 里，而是拆成“可复用单元”。最常用的是 roles，其次是 import_playbook、import_tasks、include_tasks、变量文件和模
  板。

  1. 用 Role 复用，最推荐

  Role 可以把一类操作封装成组件，比如安装 JDK、部署应用、启动服务、执行冒烟测试。

  目录示例：

  ansible/
  ├── site.yml
  ├── inventory/
  │   ├── test.ini
  │   └── prod.ini
  ├── group_vars/
  │   ├── test.yml
  │   └── prod.yml
  └── roles/
      ├── install_jdk/
      │   ├── tasks/
      │   │   └── main.yml
      │   └── defaults/
      │       └── main.yml
      ├── deploy_app/
      │   ├── tasks/
      │   │   └── main.yml
      │   ├── templates/
      │   │   └── app.conf.j2
      │   └── handlers/
      │       └── main.yml
      └── smoke_test/
          └── tasks/
              └── main.yml

  site.yml 可以这样复用多个 role：

  - name: Deploy and test application
    hosts: app_servers
    become: true

    roles:
      - install_jdk
      - deploy_app
      - smoke_test

  如果某个 role 需要参数，可以这样写：

  - name: Deploy app
    hosts: app_servers
    become: true

    roles:
      - role: deploy_app
        app_name: order-service
        app_port: 8080
        app_version: "1.2.3"

  这样 deploy_app 这个 role 可以给多个项目复用，只需要换变量。

  ———

  2. 用变量复用不同环境

  同一套 playbook 可以跑测试环境、预发环境、生产环境，只是变量不同。

  比如 group_vars/test.yml：

  app_env: test
  app_port: 8080
  app_version: "1.2.3-SNAPSHOT"
  db_host: "test-db.example.com"

  group_vars/prod.yml：

  app_env: prod
  app_port: 80
  app_version: "1.2.3"
  db_host: "prod-db.example.com"

  执行时指定不同 inventory：

  ansible-playbook -i inventory/test.ini site.yml
  ansible-playbook -i inventory/prod.ini site.yml

  这就是很典型的复用方式：Playbook 不变，变量变。

  ———

  3. 用 import_playbook 复用完整流程

  如果你有多个独立流程，比如：

  prepare-env.yml
  deploy.yml
  smoke-test.yml
  cleanup.yml

  可以用一个总 playbook 编排：

  - import_playbook: prepare-env.yml
  - import_playbook: deploy.yml
  - import_playbook: smoke-test.yml

  执行：

  ansible-playbook -i inventory/test.ini site.yml

  适合把流程拆成：

  - 环境初始化
  - 应用部署
  - 配置更新
  - 服务启动
  - 自动化检查
  - 环境清理

  ———

  4. 用 import_tasks / include_tasks 复用任务片段

  如果只是想复用一组任务，不一定要上升到 role，可以拆成 task 文件。

  例如 tasks/install_nginx.yml：

  - name: Install nginx
    ansible.builtin.yum:
      name: nginx
      state: present

  - name: Start nginx
    ansible.builtin.service:
      name: nginx
      state: started
      enabled: true

  在 playbook 中引用：

  - name: Prepare web server
    hosts: web_servers
    become: true

    tasks:
      - import_tasks: tasks/install_nginx.yml

  import_tasks 和 include_tasks 的区别：

  - import_tasks：静态导入，Ansible 解析 playbook 时就展开。
  - include_tasks：动态导入，运行时才决定加载哪个文件。

  例如动态加载：

  - name: Include OS specific tasks
    include_tasks: "tasks/{{ ansible_os_family }}.yml"

  如果目标机器是 RedHat，就加载：

  tasks/RedHat.yml

  如果是 Debian，就加载：

  tasks/Debian.yml

  ———

  5. 用模板复用配置文件

  配置文件不要写死，可以使用 Jinja2 模板。

  例如 roles/deploy_app/templates/app.conf.j2：

  server.port={{ app_port }}
  spring.profiles.active={{ app_env }}
  database.host={{ db_host }}

  任务中使用：

  - name: Render app config
    ansible.builtin.template:
      src: app.conf.j2
      dest: /opt/{{ app_name }}/app.conf
    notify: restart app

  这样不同环境只需要传不同变量，模板可以复用。

  ———

  6. 用 tag 复用部分流程

  一个 playbook 中可以给不同任务打标签。

  - name: Deploy app package
    ansible.builtin.copy:
      src: "{{ app_package }}"
      dest: "/opt/{{ app_name }}/app.jar"
    tags:
      - deploy

  - name: Run smoke test
    ansible.builtin.uri:
      url: "http://localhost:{{ app_port }}/health"
      status_code: 200
    tags:
      - smoke

  只执行部署：

  ansible-playbook -i inventory/test.ini site.yml --tags deploy

  只执行冒烟测试：

  ansible-playbook -i inventory/test.ini site.yml --tags smoke

  跳过测试：

  ansible-playbook -i inventory/test.ini site.yml --skip-tags smoke

  ———

  7. 自动化测试场景下的推荐拆法

  如果你是把 Ansible 用在自动化测试里，可以这样设计：

  roles/
  ├── prepare_env/       # 准备测试环境
  ├── deploy_service/    # 部署被测服务
  ├── init_database/     # 初始化测试数据
  ├── run_smoke_test/    # 执行冒烟检查
  ├── collect_logs/      # 收集日志
  └── cleanup_env/       # 清理环境

  主 playbook：

  - name: Automated test workflow
    hosts: test_servers
    become: true

    roles:
      - prepare_env
      - deploy_service
      - init_database
      - run_smoke_test
      - collect_logs
      - cleanup_env

  执行：

  ansible-playbook -i inventory/test.ini test-workflow.yml

  ———

  简单总结

```
  Ansible Playbook 复用主要靠这几种方式：

  - roles：复用一整套功能，最推荐。
  - import_playbook：复用完整 playbook 流程。
  - import_tasks：复用固定任务片段。
  - include_tasks：运行时动态复用任务。
  - group_vars / host_vars：通过变量区分环境。
  - templates：复用配置文件模板。
  - tags：复用部分执行流程。
  - collections：跨项目分发 roles、modules、plugins。
```

  实际项目里最常见的组合是：

  Role + 变量 + 模板 + tag

  这套方式最适合长期维护。


