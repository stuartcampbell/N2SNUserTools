from prettytable import PrettyTable
from .ldap import ADObjects
from .unix import adquery


table_order = ['displayName', 'sAMAccountName',
               'mail', 'description', 'employeeID']


def format_user_table(users, attributes=None):
    table = PrettyTable()
    names = ['Name', 'Username', 'E-Mail', 'Dep.',
             'L/G Number', 'Login']

    if attributes is not None:
        names += [a.upper() for a in attributes]

    table.field_names = names

    users = dict(sorted(
        users.items(), key=lambda item: item[1]['displayName']
    ))

    for upn, user in users.items():
        row = [user[v] for v in table_order]
        try:
            result = adquery(user['sAMAccountName'])
        except OSError:
            row += ['ERROR']
        else:
            if result['zoneEnabled'] == 'true':
                row += ['X']
            else:
                row += ['']
        if attributes is not None:
            for a in attributes:
                if a in user:
                    row += ['X']
                else:
                    row += ['']

        table.add_row(row)

    table.align['Name'] = 'l'
    table.align['Username'] = 'l'
    table.align['E-Mail'] = 'l'

    return table


def n2sn_list_group_users_as_table(server, group_search, user_search,
                                   groups):
    """List all users who are in the users group"""

    # Connect to LDAP to get group members

    with ADObjects(server, group_search, user_search,
                   authenticate=False) as ad:
        all_users = dict()
        for name, group in groups.items():
            users = ad.get_group_members_dict(group)
            for u in users:
                users[u][name] = True
                if u in all_users:
                    all_users[u] = {**all_users[u], **users[u]}
                else:
                    all_users[u] = users[u]

    return format_user_table(all_users, list(groups.keys()))


def n2sn_list_user_search_as_table(server, group_search, user_search,
                                   surname, givenname, user_type):

    with ADObjects(server, group_search, user_search,
                   authenticate=False) as ad:
        users = ad.get_user_by_surname_and_givenname_dict(
            surname, givenname, user_type
        )
    return format_user_table(users)
