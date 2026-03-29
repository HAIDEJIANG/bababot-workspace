# Ansible Modules Cheatsheet

## Package Management

### apt (Debian/Ubuntu)
```yaml

# Install package
- ansible.builtin.apt:
 name: nginx
 state: present

# Install multiple packages
name:
 - nginx, curl, git

# Install specific version
name: nginx=1.18.0-0ubuntu1

# Remove package
state: absent

# Update cache
update_cache: yes
 cache_valid_time: 3600

# Upgrade all packages
upgrade: safe # or: full, dist
```

### yum/dnf (RHEL/CentOS)
- ansible.builtin.yum:

- ansible.builtin.dnf:

# Create directory
- ansible.builtin.file:
 path: /opt/myapp
 state: directory
 owner: www-data
 group: www-data
 mode: '0755'

# Create symlink
src: /opt/myapp/current
 dest: /var/www/html
 state: link

# Delete file/directory
path: /tmp/garbage

# Touch file
path: /opt/myapp/.deployed
 state: touch
 mode: '0644'

# Copy file
- ansible.builtin.copy:
 src: files/nginx.conf
 dest: /etc/nginx/nginx.conf
 owner: root
 group: root
 backup: yes

# Copy content directly
content: |
 server {
 listen 80;
 }
 dest: /etc/nginx/conf.d/default.conf

### template
- ansible.builtin.template:
 src: nginx.conf.j2
 validate: 'nginx -t -c %s'

# Ensure line exists
- ansible.builtin.lineinfile:
 path: /etc/ssh/sshd_config
 regexp: '^PermitRootLogin'
 line: 'PermitRootLogin no'

# Add line if not exists
path: /etc/hosts
 line: '192.168.1.100 myserver'

# Remove line
path: /etc/crontab
 regexp: '^.*/opt/oldscript.sh.*$'

### blockinfile
- ansible.builtin.blockinfile:
 block: |
 Match User deploy
 PasswordAuthentication no
 PubkeyAuthentication yes
 marker: "# {mark} ANSIBLE MANAGED - deploy user"

# Create user
- ansible.builtin.user:
 name: deploy
 groups: [sudo, docker]
 shell: /bin/bash
 create_home: yes

# Remove user
name: olduser
 remove: yes # Remove home directory

### group
- ansible.builtin.group:
 name: developers

### authorized_key
- ansible.posix.authorized_key:
 user: deploy
 key: "{{ lookup('file', '~/.ssh/id_ed25519.pub') }}"
 exclusive: no # Don't remove other keys

# Start and enable service
- ansible.builtin.systemd:
 state: started
 enabled: yes

# Restart service
state: restarted

# Reload systemd daemon
daemon_reload: yes

### service (generic)
- ansible.builtin.service:

# Simple command
- ansible.builtin.command: /opt/script.sh

# With arguments
- ansible.builtin.command:
 cmd: /opt/script.sh --option value
 chdir: /opt
 creates: /opt/.done # Skip if file exists

# Pipe and redirects
- ansible.builtin.shell: cat /etc/passwd | grep deploy > /tmp/user.txt

# With environment
- ansible.builtin.shell: echo $MY_VAR
 environment:
 MY_VAR: "hello"

# Run local script on remote
- ansible.builtin.script: scripts/setup.sh
 args:
 creates: /opt/.setup-done

## Git
- ansible.builtin.git:
 repo: https://github.com/user/repo.git
 dest: /opt/myapp
 version: main # branch, tag, or commit
 force: yes # Discard local changes

## Archive

### unarchive
- ansible.builtin.unarchive:
 src: files/app.tar.gz
 remote_src: no # src is on control machine

 src: /tmp/app.tar.gz
 remote_src: yes # src is on remote

### archive
- community.general.archive:
 dest: /tmp/backup.tar.gz
 format: gz

## Networking

### ufw (Ubuntu firewall)
- community.general.ufw:
 rule: allow
 port: '22'
 proto: tcp

 state: enabled
 policy: deny
 direction: incoming

# Wait for port to be open
- ansible.builtin.wait_for:
 port: 80
 host: localhost
 timeout: 60

# Wait for file
path: /tmp/ready.txt

## Debug & Info

### debug
- ansible.builtin.debug:
 msg: "Variable value: {{ my_var }}"

 var: ansible_facts

### assert
- ansible.builtin.assert:
 that:
 - my_var is defined
 - my_var | int > 0
 fail_msg: "my_var must be a positive integer"

### stat
- ansible.builtin.stat:
 path: /etc/nginx/nginx.conf
 register: nginx_conf

 msg: "File exists"
 when: nginx_conf.stat.exists

# When
when: ansible_os_family == "Debian"

# Multiple conditions
msg: "Production Debian"
 when:
 - ansible_os_family == "Debian"
 - env == "production"

# Or conditions
msg: "Debian or Ubuntu"
 when: ansible_distribution == "Debian" or ansible_distribution == "Ubuntu"

# Simple loop
name: "{{ item }}"
 loop:

# Dict loop
name: "{{ item.name }}"
 groups: "{{ item.groups }}"
 - { name: 'alice', groups: 'sudo' }
 - { name: 'bob', groups: 'developers' }

# With index
msg: "{{ index }}: {{ item }}"
 - a, b, c
 loop_control:
 index_var: index

## Registers & Results
- ansible.builtin.command: whoami
 register: result

 msg: "Running as {{ result.stdout }}"