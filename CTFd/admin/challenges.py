from flask import current_app as app, render_template, render_template_string, url_for, jsonify
from CTFd.utils.decorators import admins_only
from CTFd.utils import binary_type
from CTFd.models import Solves, Challenges, Flags
from CTFd.models import db, Teams, Tags, Files, Tracking, Pages, Hints, Unlocks
from CTFd.plugins.challenges import get_chal_class
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.admin import admin
import os
import six


@admin.route('/admin/challenges')
@admins_only
def challenges_listing():
    challenges = Challenges.query.all()
    return render_template('admin/challenges/challenges.html', challenges=challenges)


@admin.route('/admin/chals', methods=['GET'])
@admins_only
def admin_chals():
    chals = Challenges.query.order_by(Challenges.value).all()

    json_data = {'game': []}
    for chal in chals:
        type_class = CHALLENGE_CLASSES.get(chal.type)
        type_name = type_class.name if type_class else None

        json_data['game'].append({
            'id': chal.id,
            'name': chal.name,
            'value': chal.value,
            'description': chal.description,
            'category': chal.category,
            # 'files': files,
            # 'tags': tags,
            # 'hints': hints,
            'state': chal.state,
            'max_attempts': chal.max_attempts,
            'type': chal.type,
            'type_name': type_name,
            'type_data': {
                'id': type_class.id,
                'name': type_class.name,
                'templates': type_class.templates,
                'scripts': type_class.scripts,
            }
        })

    db.session.close()
    return jsonify(json_data)


@admin.route('/admin/challenges/<int:challenge_id>')
@admins_only
def challenges_detail(challenge_id):
    challenges = dict(Challenges.query.with_entities(Challenges.id, Challenges.name).all())
    challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
    solves = Solves.query.filter_by(challenge_id=challenge.id).all()
    flags = Flags.query.filter_by(challenge_id=challenge.id).all()
    challenge_class = get_chal_class(challenge.type)

    with open(os.path.join(app.root_path, challenge_class.templates['update'].lstrip('/')), 'rb') as update:
        tpl = update.read()
        if six.PY3 and isinstance(tpl, binary_type):
            tpl = tpl.decode('utf-8')
        update_j2 = render_template_string(
            tpl,
            challenge=challenge
        )

    update_script = url_for('views.static_html', route=challenge_class.scripts['update'].lstrip('/'))
    return render_template(
        'admin/challenges/challenge.html',
        update_template=update_j2,
        update_script=update_script,
        challenge=challenge,
        challenges=challenges,
        solves=solves,
        flags=flags
    )


@admin.route('/admin/challenges/new')
@admins_only
def challenges_new():
    return render_template('admin/challenges/new.html')
