import pandas as pd, json, numpy as np

df = pd.read_excel('/mnt/user-data/uploads/TEST.xlsx', sheet_name=0)

def parse_dt(col):
    return pd.to_datetime(df[col], format='%d %b %Y, %I:%M %p', errors='coerce')

df['_raised'] = parse_dt('Escalation Date')
df['_closed'] = parse_dt('Escalation Closure Date')
df['_fr'] = parse_dt('AM FR DateTime')
df['_last'] = parse_dt('Latest AM Comment Time')
df['_reesc'] = parse_dt('Last Re-Escalated At')

agg = df.groupby('Escalation ID', as_index=False).agg(
    am=('Assigned to','first'),
    seller_id=('Seller name','first'),
    created_by=('Created By','first'),
    issue_type=('Issue Type','first'),
    subissue_type=('SubIssue Type','first'),
    raised_date=('_raised','first'),
    status=('AM Escalation ID Status','first'),
    closed_date=('_closed','first'),
    fr_date=('_fr','min'),
    last_response_date=('_last','max'),
    reesc_date=('_reesc','max'),
)
agg['seller_id'] = agg['seller_id'].fillna(agg['created_by']).fillna('Unknown')

def iso(s):
    return s.dt.strftime('%Y-%m-%dT%H:%M:%S').where(s.notna(), None)

out = pd.DataFrame({
    'ticket_id': agg['Escalation ID'],
    'am': agg['am'],
    'seller_id': agg['seller_id'],
    'issue_type': agg['issue_type'],
    'subissue_type': agg['subissue_type'],
    'raised_date': iso(agg['raised_date']),
    'status': agg['status'],
    'closed_date': iso(agg['closed_date']),
    'first_response_hours': ((agg['fr_date'] - agg['raised_date']).dt.total_seconds()/3600).round(1),
    'last_response_date': iso(agg['last_response_date']),
    'escalated': agg['reesc_date'].notna(),
    'escalation_id': np.where(agg['reesc_date'].notna(), agg['Escalation ID'], None),
})
out['first_response_hours'] = out['first_response_hours'].where(out['first_response_hours'].notna(), None)

records = out.to_dict(orient='records')
for r in records:
    for k,v in r.items():
        if isinstance(v, float) and np.isnan(v):
            r[k] = None
        if isinstance(v, np.bool_):
            r[k] = bool(v)

data = {
    'last_updated': '2026-07-05T13:25:00+05:30',
    'ams': sorted(df['Assigned to'].dropna().unique().tolist()),
    'issue_types': sorted(df['Issue Type'].dropna().unique().tolist()),
    'tickets': records
}

with open('/home/claude/ekart-dashboard/data.json','w') as f:
    json.dump(data, f)

print('raw rows:', len(df), '-> deduped tickets:', len(records))
