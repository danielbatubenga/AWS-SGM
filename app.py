from flask import Flask, request, redirect, url_for, render_template
import boto3

app = Flask(__name__)
ec2 = boto3.client('ec2', region_name='us-east-1')  # Substitua 'your-region' pela sua região

@app.route('/')
def index():
    security_groups = ec2.describe_security_groups()['SecurityGroups']
    return render_template('index.html', security_groups=security_groups)

@app.route('/edit/<group_id>', methods=['GET', 'POST'])
def edit_security_group(group_id):
    security_group = ec2.describe_security_groups(GroupIds=[group_id])['SecurityGroups'][0]

    if request.method == 'POST':
        action = request.form['action']
        protocol = request.form['protocol']
        port_range = request.form['port_range']
        from_port, to_port = map(int, port_range.split('-'))
        source = request.form['source']

        if action == 'add_ingress':
            name = request.form['name']
            ec2.authorize_security_group_ingress(
                GroupId=group_id,
                IpPermissions=[
                    {
                        'IpProtocol': protocol,
                        'FromPort': from_port,
                        'ToPort': to_port,
                        'IpRanges': [{'CidrIp': source, 'Description': name}]
                    }
                ]
            )
            return redirect(url_for('edit_security_group', group_id=group_id, notification='rule_added'))

        elif action == 'remove_ingress':
            ec2.revoke_security_group_ingress(
                GroupId=group_id,
                IpPermissions=[
                    {
                        'IpProtocol': protocol,
                        'FromPort': from_port,
                        'ToPort': to_port,
                        'IpRanges': [{'CidrIp': source}]
                    }
                ]
            )
            return redirect(url_for('edit_security_group', group_id=group_id, notification='rule_removed'))

    return render_template('edit.html', security_group=security_group)

if __name__ == '__main__':
    app.run(debug=True)
