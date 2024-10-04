FROM python:3.10-slim
RUN mkdir /app
COPY requirements.txt /app
WORKDIR /app
RUN pip3 install -r requirements.txt
ENV ANSIBLE_HOST_KEY_CHECKING=False
CMD ["python", "ansible-playbook -i netbox_inv.yml show_version.yml"]
# To test:
# export EXTRA_VARS='{"target_hosts": "all"}'
# docker run -e EXTRA_VARS evolvere/netbox-ansible-webinar:0.1
