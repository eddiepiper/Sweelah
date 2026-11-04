"""Encrypted LOCAL SYNTHETIC ONLY persistence boundary for the RetirePilot prototype.

This is not an authenticated, multi-tenant production data platform. No remote API.
Full-profile and action/memory contents are encrypted with a Fernet key supplied via
RETIREPILOT_VAULT_KEY; never store keys beside the database. SQLite metadata is
not encrypted and the process owner can access the running process.
"""
from __future__ import annotations
import os, json, sqlite3, hashlib, hmac, re
from datetime import datetime, timezone
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
from .core import validate, age_on, ValidationError
from datetime import date

PURPOSES={'household_planning','local_memory','action_tracking'}
TRANSITIONS={'suggested':{'approved'},'approved':{'in_progress','cancelled'},
             'in_progress':{'reported_complete','cancelled'},'reported_complete':{'simulated_verified','in_progress'},
             'simulated_verified':set(),'cancelled':set()}

class VaultError(RuntimeError):pass

class LocalVault:
    def __init__(self, path, *, key=None):
        key=key or os.getenv('RETIREPILOT_VAULT_KEY')
        if not key:raise VaultError('RETIREPILOT_VAULT_KEY required; never persist without encryption')
        try:self.cipher=Fernet(key if isinstance(key,bytes) else key.encode())
        except (ValueError,TypeError) as exc:raise VaultError('Invalid encryption key') from exc
        self.path=Path(path).expanduser()
        self.path.parent.mkdir(parents=True,exist_ok=True)
        os.chmod(self.path.parent,0o700)
        if self.path.exists() and (self.path.stat().st_mode & 0o077):raise VaultError('Database permissions must exclude group/others')
        self.db=sqlite3.connect(str(self.path))
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA secure_delete=ON')
        self.db.execute('PRAGMA journal_mode=DELETE')
        self.db.execute('CREATE TABLE IF NOT EXISTS consent (profile_id TEXT, person_id TEXT, purpose TEXT, granted_at TEXT, revoked_at TEXT, PRIMARY KEY(profile_id,person_id,purpose))')
        self.db.execute('CREATE TABLE IF NOT EXISTS profile (id TEXT PRIMARY KEY, cipher BLOB NOT NULL, updated_at TEXT NOT NULL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS action (id TEXT PRIMARY KEY, profile_id TEXT NOT NULL REFERENCES profile(id) ON DELETE CASCADE, cipher BLOB NOT NULL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, profile_id TEXT NOT NULL REFERENCES profile(id) ON DELETE CASCADE, cipher BLOB NOT NULL, created_at TEXT NOT NULL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT, profile_digest TEXT, operation TEXT)')
        self.db.commit();os.chmod(self.path,0o600)

    def close(self):self.db.close()
    def _now(self):return datetime.now(timezone.utc).isoformat()
    def _digest(self,pid):return hmac.new(self.cipher._signing_key,pid.encode(),hashlib.sha256).hexdigest()[:20]
    def _audit(self,pid,event):
        self.db.execute('INSERT INTO audit(time,profile_digest,operation) VALUES(?,?,?)',(self._now(),self._digest(pid),event))
    def _seal(self,value):return self.cipher.encrypt(json.dumps(value,ensure_ascii=False,sort_keys=True).encode())
    def _open(self,blob):
        try:return json.loads(self.cipher.decrypt(blob))
        except (InvalidToken,ValueError) as exc:raise VaultError('Cannot decrypt record (wrong key or tampering)') from exc
    def grant_consent(self,profile_id,person_id,purpose,*,explicit:bool=False):
        if not profile_id.startswith('RP-SYNTH-'):raise VaultError('Synthetic records only')
        if purpose not in PURPOSES or explicit is not True:raise VaultError('Explicit specific-purpose consent required')
        self.db.execute('INSERT OR REPLACE INTO consent VALUES(?,?,?,?,NULL)',(profile_id,person_id,purpose,self._now()))
        self._audit(profile_id,'consent_granted:'+purpose);self.db.commit()
    def _has_consent(self,profile_id,person_id,purpose):
        return self.db.execute('SELECT 1 FROM consent WHERE profile_id=? AND person_id=? AND purpose=? AND revoked_at IS NULL',(profile_id,person_id,purpose)).fetchone() is not None
    def revoke_consent(self,profile_id,person_id,purpose):
        self.db.execute('UPDATE consent SET revoked_at=? WHERE profile_id=? AND person_id=? AND purpose=?',(self._now(),profile_id,person_id,purpose))
        # Fail-closed: remove whole profile and associated actions/memory if consent required for analysis was revoked.
        if purpose=='household_planning' and self.db.execute('SELECT 1 FROM profile WHERE id=?',(profile_id,)).fetchone():
            self.db.execute('DELETE FROM profile WHERE id=?',(profile_id,))
            self._audit(profile_id,'profile_deleted_due_to_consent_revocation')
        elif purpose in ('local_memory','action_tracking'):
            table='memory' if purpose=='local_memory' else 'action'
            for rid,cipher in self.db.execute(f'SELECT id,cipher FROM {table} WHERE profile_id=?',(profile_id,)).fetchall():
                if self._open(cipher).get('person_id')==person_id:
                    self.db.execute(f'DELETE FROM {table} WHERE id=?',(rid,))
            self._audit(profile_id,'consented_content_deleted:'+purpose)
        self._audit(profile_id,'consent_revoked:'+purpose);self.db.commit()
    def put_profile(self,profile):
        pid=profile.get('id','')
        if not isinstance(pid,str) or not pid.startswith('RP-SYNTH-'):raise VaultError('Only synthetic profiles allowed')
        validate(profile)
        persons={p['id']:p for p in profile['persons']}
        for person in persons.values():
            if age_on(person['dob'],date.fromisoformat(profile['as_of']))>=18 and not self._has_consent(pid,person['id'],'household_planning'):
                raise VaultError('Independent household-planning consent required for each adult, including primary')
        self.db.execute('INSERT INTO profile(id,cipher,updated_at) VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET cipher=excluded.cipher,updated_at=excluded.updated_at',(pid,self._seal(profile),self._now()))
        self._audit(pid,'profile_upserted');self.db.commit()
    def get_profile(self,profile_id):
        row=self.db.execute('SELECT cipher FROM profile WHERE id=?',(profile_id,)).fetchone()
        if not row:raise VaultError('Profile not found')
        profile=self._open(row[0]);
        if any(age_on(p['dob'],date.fromisoformat(profile['as_of']))>=18 and not self._has_consent(profile_id,p['id'],'household_planning') for p in profile['persons']):
            raise VaultError('Required consent withdrawn or missing')
        return profile
    def save_memory(self,profile_id,person_id,memory_id,summary):
        if not self._has_consent(profile_id,person_id,'local_memory'):raise VaultError('Memory consent required')
        self.get_profile(profile_id)
        if not isinstance(summary,str) or not 1<=len(summary)<=300:raise VaultError('Memory summary must be 1-300 characters')
        # Strict minimal memory: summaries must be user reviewed and are NOT treated as verified facts.
        record={'person_id':person_id,'summary':summary,'evidence':'user_reported_unverified'}
        self.db.execute('INSERT INTO memory VALUES(?,?,?,?)',(memory_id,profile_id,self._seal(record),self._now()))
        self._audit(profile_id,'memory_saved');self.db.commit()
    def list_memory(self,profile_id,person_id):
        if not self._has_consent(profile_id,person_id,'local_memory'):raise VaultError('Memory consent required')
        self.get_profile(profile_id)
        return [self._open(row[0]) for row in self.db.execute('SELECT cipher FROM memory WHERE profile_id=?',(profile_id,)) if self._open(row[0])['person_id']==person_id]
    def create_action(self,profile_id,person_id,action_id,title,reason):
        if not self._has_consent(profile_id,person_id,'action_tracking'):raise VaultError('Action tracking consent required')
        self.get_profile(profile_id)
        if not title or len(title)>160 or len(reason)>500:raise VaultError('Action field limits exceeded')
        rec={'id':action_id,'person_id':person_id,'title':title,'reason':reason,'status':'suggested','history':[{'status':'suggested','at':self._now()}], 'verified_complete':False}
        self.db.execute('INSERT INTO action VALUES(?,?,?)',(action_id,profile_id,self._seal(rec)))
        self._audit(profile_id,'action_created');self.db.commit()
        return rec
    def transition_action(self,profile_id,action_id,new_status,*,actor,approval=False,evidence_ref=None,verifier=None):
        row=self.db.execute('SELECT cipher FROM action WHERE id=? AND profile_id=?',(action_id,profile_id)).fetchone()
        if not row:raise VaultError('Action not found')
        rec=self._open(row[0]);self.get_profile(profile_id)
        if not self._has_consent(profile_id,rec['person_id'],'action_tracking'):raise VaultError('Action consent missing')
        old=rec['status']
        if new_status not in TRANSITIONS.get(old,set()):raise VaultError('Invalid state transition')
        if new_status=='approved' and approval is not True:raise VaultError('Explicit user approval required')
        # Local synthetic profiles cannot be genuinely verified against official
        # providers.  A text label for a verifier is not authentication.
        if new_status=='verified':
            raise VaultError('Real-world verification unavailable without an authenticated evidence provider')
        if new_status=='simulated_verified':
            if not evidence_ref or not verifier or actor==verifier or not str(evidence_ref).lower().startswith('synthetic-'):
                raise VaultError('Simulation requires synthetic evidence and a distinct mock verifier')
            rec['verified_complete']=False
            rec['simulation']={'ref':evidence_ref,'mock_verifier':verifier,'simulation_only':True}

        if new_status=='reported_complete':rec['reported_by']=actor
        rec['status']=new_status;rec['history'].append({'status':new_status,'actor':actor,'at':self._now()})
        self.db.execute('UPDATE action SET cipher=? WHERE id=?',(self._seal(rec),action_id))
        self._audit(profile_id,'action_transition:'+new_status);self.db.commit()
        return rec
    def share_household_records(self,profile_id,recipient_person_id,*,identity_evidence=None,consent_evidence=None):
        """Production sharing is disabled: no authenticated per-adult identity and consent provider.

        A synthetic consent checkbox, username or self-declared evidence must
        never be mistaken for authentication. This method intentionally refuses
        ALL sharing until a separately reviewed external verification service exists.
        """
        raise VaultError('Household financial record sharing blocked: independent adult identity and consent verification unavailable')

    def delete_profile(self,profile_id):
        self.db.execute('DELETE FROM profile WHERE id=?',(profile_id,))
        self.db.execute('DELETE FROM consent WHERE profile_id=?',(profile_id,))
        self._audit(profile_id,'profile_deleted');self.db.commit()
    def list_audit_events(self):
        return self.db.execute('SELECT time, profile_digest, operation FROM audit ORDER BY id').fetchall()
