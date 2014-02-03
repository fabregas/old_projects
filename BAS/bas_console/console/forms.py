from django import forms
import re
from models import *

class ModifyNodeForm(forms.Form):
    logic_name = forms.CharField(max_length=255)
    host = forms.CharField(max_length=50)

    def clean_host(self):
        host = self.cleaned_data['host']
        m = re.match("(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", host)
        if m:
            values = []
            for item in m.groups():
                item = int(item)
                if item > 255 or item < 0:
                    raise forms.ValidationError("IP address is invalid!")
                values.append(str(item))

            host = '.'.join(values)

        if not self.node_id:
            node = BasClusterNode.objects.filter(hostname=host)
            if node:
                raise forms.ValidationError("Node with IP address %s is already present in cluster!"%host)

        return host

    def set_nodeid(self, nodeid):
        self.node_id = nodeid



class ModifyClusterForm(forms.Form):
    cluster_sid = forms.CharField(max_length=100)
    cluster_name = forms.CharField(max_length=255)

    def clean_cluster_sid(self):
        sid = self.cleaned_data['cluster_sid']

        if not self.cluster_id:
            cluster = BasCluster.objects.filter(cluster_sid=sid)
            if cluster:
                raise forms.ValidationError("Cluster with SID %s is already exists!"%sid)

        return sid

    def set_clusterid(self, clusterid):
        self.cluster_id = clusterid


class ModifyConfigForm(forms.Form):
    CHOICES = (
        (1, 'String'),
        (2, 'Integer'),
        (3, 'Boolean'),
        (4, 'Hidden string')
    )
    param_name = forms.CharField(max_length=255)
    param_type = forms.ChoiceField(CHOICES)
    param_value = forms.CharField(required=False, max_length=1024)
    description = forms.CharField(required=False, max_length=1024)

    def clean_param_value(self):
        param_value = self.cleaned_data['param_value']
        param_type = int(self.cleaned_data['param_type'])

        if param_type in [1,4]: #string
            pass
        elif param_type == 2: #integer
            try:
                int(param_value)
            except:
                raise forms.ValidationError("Integer value is expected!")
        elif param_type == 3: #boolean
            if param_value.lower().strip() not in ['true', 'false']:
                raise forms.ValidationError("Boolean value must be true or false")

        return param_value

