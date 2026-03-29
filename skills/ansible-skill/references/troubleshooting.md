# Ansible Troubleshooting Guide

## Connection Issues

### "Permission denied" / SSH Key Issues
```bash

# Test SSH manually first
ssh -v user@host

# Check key permissions (must be 600)
chmod 600 ~/.ssh/id_*
chmod 644 ~/.ssh/*.pub
chmod 700 ~/.ssh

# Specify key explicitly
ansible all -i inventory -m ping --private-key=~/.ssh/mykey

# Debug Ansible connection
ansible all -i inventory -m ping -vvv
```

# Option 1: Add host key manually
ssh-keyscan -H hostname >> ~/.ssh/known_hosts

# In ansible.cfg:
[defaults]
host_key_checking = False

# Or per-command:
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook site.yml

# Check basic connectivity
ping hostname
nc -zv hostname 22

# Check firewall
sudo ufw status
sudo iptables -L

# Try with specific port
ansible all -i inventory -m ping -e "ansible_port=2222"

### Python Interpreter Not Found
```yaml

# Specify in inventory
all:
 vars:
 ansible_python_interpreter: /usr/bin/python3

# Or per-host
myhost:

# Option 1: Ask for password
ansible-playbook site.yml --ask-become-pass

# /etc/sudoers.d/myuser:
myuser ALL=(ALL) NOPASSWD:ALL

# Option 3: Set in inventory
ansible_become_pass: "{{ vault_sudo_password }}"

# Interactive password prompt
ansible-playbook site.yml --ask-vault-pass

# Password file
ansible-playbook site.yml --vault-password-file ~/.vault_pass

# Multiple vault passwords
ansible-playbook site.yml --vault-id dev@~/.vault_dev --vault-id prod@~/.vault_prod

# View encrypted file
ansible-vault view group_vars/all/vault.yml

# Edit encrypted file
ansible-vault edit group_vars/all/vault.yml

# Rekey (change password)
ansible-vault rekey group_vars/all/vault.yml

# Install missing collection
ansible-galaxy collection install community.general

# List installed collections
ansible-galaxy collection list

# Install on target machine
ansible myhost -m apt -a "name=python3-xyz state=present" --become

# Or install via pip on target
ansible myhost -m pip -a "name=xyz state=present"

# Check syntax
ansible-playbook site.yml --syntax-check

# Lint playbook
pip install ansible-lint
ansible-lint site.yml

# Check if defined before use
- debug:
 msg: "{{ my_var }}"
 when: my_var is defined

# Provide default value
msg: "{{ my_var | default('fallback') }}"

# Test template rendering
ansible localhost -m template -a "src=template.j2 dest=/dev/stdout"

# Increasing verbosity levels
ansible-playbook site.yml -v # Basic
ansible-playbook site.yml -vv # More
ansible-playbook site.yml -vvv # Connection debug
ansible-playbook site.yml -vvvv # Maximum

# Step mode - confirm each task
ansible-playbook site.yml --step

# Start at specific task
ansible-playbook site.yml --start-at-task="Install nginx"

# List tasks without running
ansible-playbook site.yml --list-tasks

# List hosts that would be affected
ansible-playbook site.yml --list-hosts

# Print variable
- ansible.builtin.debug:
 var: my_var

# Print message
msg: "Value is {{ my_var }}"

# Print all facts
var: ansible_facts

# Conditional debug
msg: "This is production!"
 when: env == "production"

### Register and Check
- name: Run command
 ansible.builtin.command: /opt/script.sh
 register: result
 ignore_errors: yes

- name: Show result
 ansible.builtin.debug:
 var: result

- name: Show specific parts
 msg: |
 stdout: {{ result.stdout }}
 stderr: {{ result.stderr }}
 rc: {{ result.rc }}

# Disable fact gathering if not needed
- hosts: all
 gather_facts: no

# Gather only needed facts
gather_subset:
 - network

# ansible.cfg:
[ssh_connection]
pipelining = True

# Increase parallelism
forks = 20

# Use ControlMaster (connection reuse)
ssh_args = -o ControlMaster=auto -o ControlPersist=60s

## Common Error Messages

### "Aborting, target uses selinux but python bindings aren't installed"
- name: Install SELinux Python bindings
 ansible.builtin.yum:
 name:
 - libselinux-python3
 - python3-policycoreutils
 state: present

# Add become: yes
- name: Copy file to protected location
 ansible.builtin.copy:
 src: file.txt
 dest: /etc/myfile.txt
 become: yes

# In inventory or playbook:
ansible_ssh_timeout: 30

# Or command line:
ansible-playbook site.yml -T 30

### "Error while fetching server API version"
Usually Docker-related:

# Ensure user is in docker group
- name: Add user to docker group
 ansible.builtin.user:
 name: "{{ ansible_user }}"
 groups: docker
 append: yes

# Ansible creates .retry file with failed hosts
ansible-playbook site.yml --limit @site.retry

# Use block/rescue
- name: Deploy with rollback
 block:
 - name: Deploy new version
 ansible.builtin.unarchive:
 src: app-v2.tar.gz
 dest: /opt/app
 - name: Restart service
 ansible.builtin.systemd:
 name: myapp
 state: restarted
 rescue:
 - name: Rollback to previous version
 ansible.builtin.command: /opt/rollback.sh
 - name: Notify failure
 msg: "Deployment failed, rolled back"