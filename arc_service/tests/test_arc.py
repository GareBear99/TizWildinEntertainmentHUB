from pathlib import Path
import shutil
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app
from app.services.bootstrap_service import DEMO_RELEASES, DEMO_ENTITLEMENTS
from app.services.store import load_release_manifests, save_auth_tokens, save_entitlements, save_install_receipts, save_install_scans, save_settings, save_webhooks, save_seats, save_release_manifests

client = TestClient(app)
TEST_INSTALL_ROOT = Path('/mnt/data/hub_v10_test_installs')


def reset_state():
    save_entitlements(DEMO_ENTITLEMENTS)
    save_seats({})
    save_install_scans([])
    save_install_receipts([])
    save_webhooks([])
    save_auth_tokens({})
    save_settings({})
    save_release_manifests(DEMO_RELEASES)
    if TEST_INSTALL_ROOT.exists():
        shutil.rmtree(TEST_INSTALL_ROOT)


def setup_function():
    reset_state()


def test_health():
    assert client.get('/health').json()['status'] == 'ok'


def test_catalog_present():
    body = client.get('/catalog').json()
    assert any(p['productId'] == 'therum' for p in body['products'])


def test_mock_login_works():
    body = client.post('/auth/mock-login', json={'accountId': 'demo_account', 'machineId': 'mac_alpha'}).json()
    assert body['approved'] is True
    assert body['token'].startswith('mock_')


def test_free_product_runtime_allowed():
    body = client.post('/validate-runtime', json={'accountId': 'free_account', 'machineId': 'mac_alpha', 'productId': 'freeeq8', 'edition': 'standard', 'runtimeVersion': '0.1.0'}).json()
    assert body['approved'] is True


def test_paid_product_denied_when_not_owned():
    body = client.post('/validate-runtime', json={'accountId': 'free_account', 'machineId': 'mac_beta', 'productId': 'therum', 'edition': 'pro', 'runtimeVersion': '0.1.0'}).json()
    assert body['approved'] is False
    assert body['reason'] == 'not_owned'


def test_account_summary_includes_stats():
    body = client.get('/account-summary/demo_account').json()
    assert body['stats']['maxSeats'] == 3
    assert body['entitlements']['ownsEveryVST'] is True


def test_install_missing_proposal_returns_actions():
    body = client.post('/proposal', json={'proposalId': 'p1', 'type': 'install_missing', 'accountId': 'demo_account', 'machineId': 'mac1', 'requestedProducts': ['therum', 'freeeq8']}).json()
    assert body['approved'] is True
    assert len(body['actions']) == 2


def test_install_plan_marks_update_available_after_scan():
    client.post('/install-scan', json={'accountId': 'demo_account', 'machineId': 'mac1', 'products': [{'productId': 'therum', 'localVersion': '0.8.0', 'runtimeVersion': '0.8.0', 'installState': 'installed', 'binaryPresent': False, 'sourcePresent': True}]})
    body = client.post('/install-plan', json={'accountId': 'demo_account', 'machineId': 'mac1', 'requestedProducts': ['therum']}).json()
    assert body['approved'] is True
    assert body['actions'][0]['action'] == 'update_available'


def test_download_plan_contains_sha():
    client.post('/releases/stage-local', params={'channel': 'stable'})
    body = client.post('/download-plan', json={'accountId': 'demo_account', 'machineId': 'mac1', 'requestedProducts': ['therum']}).json()
    assert body['approved'] is True
    assert body['downloads'][0]['sha256']
    assert body['downloads'][0]['artifactPath']
    assert 'verify_sha256' in body['downloads'][0]['steps']


def test_record_receipt_creates_entry():
    client.post('/releases/stage-local', params={'channel': 'stable'})
    body = client.post('/record-receipt', json={'accountId': 'demo_account', 'machineId': 'mac1', 'requestedProducts': ['therum']}).json()
    assert body['approved'] is True
    receipts = client.get('/receipts/demo_account').json()['receipts']
    assert len(receipts) >= 1


def test_webhook_grants_extra_seats_when_signature_matches():
    body = client.post('/webhooks/ingest', json={'provider': 'stripe', 'eventType': 'checkout.session.completed', 'signature': 'arc_demo_secret', 'payload': {'accountId': 'demo_account', 'grant': 'extra_seats', 'quantity': 4}}).json()
    assert body['accepted'] is True
    summary = client.get('/account-summary/demo_account').json()
    assert summary['entitlements']['extraSeatQuantity'] == 4


def test_stage_local_updates_manifest_artifact_path():
    body = client.post('/releases/stage-local', params={'channel': 'stable'}).json()
    staged = body['staged']
    assert staged['therum']['artifactPath'].endswith('.zip')
    manifests = load_release_manifests()
    assert manifests['therum']['artifactPath'].endswith('.zip')


def test_owned_catalog_filters_for_free_account():
    body = client.get('/catalog/owned/free_account').json()
    ids = {p['productId'] for p in body['products']}
    assert 'freeeq8' in ids
    assert 'therum' not in ids


def test_mock_login_and_validate_and_logout_cycle():
    login = client.post('/auth/mock-login', json={'accountId': 'demo_account', 'machineId': 'mac_alpha'}).json()
    token = login['token']
    validate = client.post('/auth/validate', json={'token': token}).json()
    assert validate['approved'] is True
    logout = client.post('/auth/logout', json={'token': token}).json()
    assert logout['approved'] is True
    failed = client.post('/auth/validate', json={'token': token})
    assert failed.status_code == 401


def test_execute_downloads_dry_run_records_receipt():
    client.post('/releases/stage-local', params={'channel': 'stable'})
    body = client.post('/execute-downloads', json={'accountId': 'demo_account', 'machineId': 'mac_exec', 'requestedProducts': ['therum'], 'channel': 'stable', 'dryRun': True, 'installRoot': str(TEST_INSTALL_ROOT)}).json()
    assert body['approved'] is True
    assert body['executed'][0]['status'] == 'dry_run_planned'


def test_execute_downloads_apply_installs_and_updates_machine_inventory():
    client.post('/releases/stage-local', params={'channel': 'stable'})
    body = client.post('/execute-downloads', json={'accountId': 'demo_account', 'machineId': 'mac_apply', 'requestedProducts': ['therum'], 'channel': 'stable', 'dryRun': False, 'installRoot': str(TEST_INSTALL_ROOT)}).json()
    assert body['approved'] is True
    assert body['executed'][0]['status'] == 'executed'
    machines = client.get('/machines/demo_account').json()['machines']
    target = next(m for m in machines if m['machineId'] == 'mac_apply')
    assert target['productCount'] == 1
    assert target['installedProducts'][0]['productId'] == 'therum'


def test_repair_and_uninstall_cycle():
    client.post('/releases/stage-local', params={'channel': 'stable'})
    client.post('/execute-downloads', json={'accountId': 'demo_account', 'machineId': 'mac_fix', 'requestedProducts': ['therum'], 'channel': 'stable', 'dryRun': False, 'installRoot': str(TEST_INSTALL_ROOT)})
    repair = client.post('/repair', json={'accountId': 'demo_account', 'machineId': 'mac_fix', 'productId': 'therum', 'channel': 'stable', 'installRoot': str(TEST_INSTALL_ROOT)}).json()
    assert repair['approved'] is True
    uninstall = client.post('/uninstall', json={'accountId': 'demo_account', 'machineId': 'mac_fix', 'productId': 'therum'}).json()
    assert uninstall['approved'] is True


def test_backup_export_and_restore_round_trip():
    export = client.post('/backups/export', params={'tag': 'testcase'}).json()
    assert export['approved'] is True
    path = export['path']
    save_entitlements({'mutated': {'accountId': 'mutated', 'ownsEveryVST': False, 'ownedProducts': [], 'ownedBundles': [], 'extraSeatQuantity': 0, 'billingState': 'active'}})
    restore = client.post('/backups/restore', json={'path': path}).json()
    assert restore['approved'] is True
    summary = client.get('/account-summary/demo_account').json()
    assert summary['accountId'] == 'demo_account'


def test_preflight_returns_warnings_and_plans():
    client.post('/releases/stage-local', params={'channel': 'stable'})
    body = client.post('/preflight', json={'accountId': 'demo_account', 'machineId': 'mac_pre', 'requestedProducts': ['therum'], 'channel': 'stable'}).json()
    assert body['approved'] is True
    assert 'installPlan' in body
    assert 'downloadPlan' in body


def test_release_query_filters_channel():
    stable = client.get('/releases', params={'channel': 'stable'}).json()
    beta = client.get('/releases', params={'channel': 'beta'}).json()
    assert 'therum' in stable
    assert 'wurp' in beta
    assert 'wurp' not in stable


def test_diagnostics_export_writes_file():
    body = client.get('/diagnostics/export/demo_account').json()
    assert body['approved'] is True
    assert Path(body['path']).exists()


def test_launchpad_endpoint_summarizes_installables():
    client.post('/releases/stage-local', params={'channel': 'stable'})
    body = client.get('/launchpad/demo_account', params={'machine_id': 'mac_demo', 'channel': 'stable'}).json()
    assert body['approved'] is True
    assert body['overview']['downloadableCount'] >= 1
    assert 'stable' in body['releaseChannels']


def test_demo_bootstrap_restores_demo_state_and_stages_artifacts():
    save_entitlements({'broken': {'accountId': 'broken', 'ownsEveryVST': False, 'ownedProducts': [], 'ownedBundles': [], 'extraSeatQuantity': 0, 'billingState': 'inactive'}})
    body = client.post('/demo/bootstrap', params={'stage_artifacts': 'true'}).json()
    assert body['approved'] is True
    assert 'demo_account' in body['accounts']
    assert body['stagedCount'] >= 1


def test_seat_release_flow():
    runtime = client.post('/validate-runtime', json={'accountId': 'demo_account', 'machineId': 'mac_seat', 'productId': 'therum', 'edition': 'standard', 'runtimeVersion': '1.0.0'}).json()
    seat_id = runtime['seat']['seatId']
    released = client.post('/seats/release', json={'accountId': 'demo_account', 'seatId': seat_id}).json()
    assert released['approved'] is True


def test_rollback_requires_previous_version_then_succeeds():
    client.post('/releases/stage-local', params={'channel': 'stable'})
    client.post('/execute-downloads', json={'accountId': 'demo_account', 'machineId': 'mac_rb', 'requestedProducts': ['therum'], 'channel': 'stable', 'dryRun': False, 'installRoot': str(TEST_INSTALL_ROOT)})
    manifests = load_release_manifests()
    manifests['therum']['latestVersion'] = '1.1.0'
    save_release_manifests(manifests)
    client.post('/releases/stage-local', params={'channel': 'stable'})
    client.post('/execute-downloads', json={'accountId': 'demo_account', 'machineId': 'mac_rb', 'requestedProducts': ['therum'], 'channel': 'stable', 'dryRun': False, 'installRoot': str(TEST_INSTALL_ROOT)})
    rollback = client.post('/rollback', json={'accountId': 'demo_account', 'machineId': 'mac_rb', 'productId': 'therum'}).json()
    assert rollback['approved'] is True
    assert rollback['rolledBackTo'] == '1.0.0'


def test_settings_round_trip_and_launchpad_includes_settings():
    saved = client.post('/settings', json={
        'accountId': 'demo_account',
        'machineId': 'mac_custom',
        'preferredChannel': 'beta',
        'theme': 'dark',
        'arcBaseUrl': 'http://127.0.0.1:8000',
        'installRoot': '/tmp/custom_installs',
        'autoStageOnBootstrap': True,
        'autoBackupBeforeExecute': False,
    }).json()
    assert saved['machineId'] == 'mac_custom'
    launchpad = client.get('/launchpad/demo_account', params={'machine_id': 'mac_custom', 'channel': 'beta'}).json()
    assert launchpad['settings']['preferredChannel'] == 'beta'


def test_activity_feed_returns_receipts_and_webhooks():
    client.post('/releases/stage-local', params={'channel': 'stable'})
    client.post('/execute-downloads', json={'accountId': 'demo_account', 'machineId': 'mac_feed', 'requestedProducts': ['therum'], 'channel': 'stable', 'dryRun': True, 'installRoot': str(TEST_INSTALL_ROOT)})
    client.post('/webhooks/ingest', json={'provider': 'stripe', 'eventType': 'checkout.session.completed', 'signature': 'arc_demo_secret', 'payload': {'accountId': 'demo_account', 'grant': 'extra_seats', 'quantity': 1}})
    body = client.get('/activity/demo_account').json()
    assert body['count'] >= 2


def test_readiness_endpoint_reports_ready_after_stage():
    client.post('/releases/stage-local', params={'channel': 'stable'})
    body = client.get('/readiness/demo_account').json()
    assert body['approved'] is True
    assert body['ready'] is True

def test_sync_endpoint_returns_actionable_summary():
    client.post('/releases/stage-local', params={'channel': 'stable'})
    body = client.post('/sync', json={'accountId': 'demo_account', 'machineId': 'mac_sync', 'requestedProducts': ['therum'], 'channel': 'stable'}).json()
    assert body['approved'] is True
    assert body['nextAction'] in {'execute', 'idle'}
    assert body['counts']['downloads'] >= 1


def test_support_bundle_creates_zip():
    body = client.get('/support/bundle/demo_account', params={'machine_id': 'mac_demo', 'channel': 'stable'}).json()
    assert body['approved'] is True
    assert Path(body['path']).exists()
    assert body['path'].endswith('.zip')


def test_audit_endpoint_returns_score_and_grade():
    client.post('/releases/stage-local', params={'channel': 'stable'})
    body = client.get('/audit/demo_account', params={'machine_id': 'mac_demo', 'channel': 'stable'}).json()
    assert body['approved'] is True
    assert isinstance(body['score'], int)
    assert body['grade'] in {'A', 'B', 'C', 'D'}


def test_local_register_login_refresh_cycle():
    register = client.post('/auth/register', json={'email': 'gary@example.com', 'password': 'Secret123!', 'displayName': 'Gary', 'machineId': 'mac_local'}).json()
    assert register['approved'] is True
    assert register['accountId'].startswith('acct_')
    token = register['token']
    me = client.get('/auth/me', params={'token': token}).json()
    assert me['email'] == 'gary@example.com'
    login = client.post('/auth/login', json={'email': 'gary@example.com', 'password': 'Secret123!', 'machineId': 'mac_local'}).json()
    assert login['approved'] is True
    refreshed = client.post('/auth/refresh', json={'refreshToken': login['refreshToken'], 'machineId': 'mac_local'}).json()
    assert refreshed['approved'] is True
    assert refreshed['token'].startswith('arc_')


def test_local_checkout_updates_entitlements():
    register = client.post('/auth/register', json={'email': 'buyer@example.com', 'password': 'Secret123!', 'displayName': 'Buyer', 'machineId': 'mac_store'}).json()
    account_id = register['accountId']
    checkout = client.post('/billing/checkout-session', json={'accountId': account_id, 'productId': 'paintmask', 'quantity': 1}).json()
    assert checkout['approved'] is True
    complete = client.post('/billing/checkout-complete', json={'accountId': account_id, 'productId': 'paintmask', 'quantity': 1}).json()
    assert complete['approved'] is True
    summary = client.get(f'/account-summary/{account_id}').json()
    assert 'paintmask' in summary['entitlements']['ownedProducts']


def test_release_import_and_remote_file_execute():
    client.post('/demo/bootstrap', params={'stage_artifacts': 'true'})
    staged = client.post('/releases/stage-local', params={'channel': 'stable'}).json()['staged']
    therum = staged['therum']
    import json, tempfile
    payload = {
        'paintmask': {
            'productId': 'paintmask',
            'channel': 'stable',
            'latestVersion': '2.0.0',
            'artifactMode': 'zip',
            'artifactUrl': f"file://{therum['artifactPath']}",
            'artifactPath': '',
            'sha256': therum['sha256'],
            'signature': 'arc-demo-signed-local',
            'notes': 'Imported test artifact',
        }
    }
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as fh:
        json.dump(payload, fh)
        temp_path = fh.name
    imported = client.post('/releases/import', json={'source': temp_path, 'replaceExisting': False}).json()
    assert imported['approved'] is True
    register = client.post('/auth/register', json={'email': 'importer@example.com', 'password': 'Secret123!', 'displayName': 'Importer', 'machineId': 'mac_import'}).json()
    account_id = register['accountId']
    complete = client.post('/billing/checkout-complete', json={'accountId': account_id, 'productId': 'paintmask', 'quantity': 1}).json()
    assert complete['approved'] is True
    body = client.post('/execute-downloads', json={'accountId': account_id, 'machineId': 'mac_import', 'requestedProducts': ['paintmask'], 'channel': 'stable', 'dryRun': False, 'installRoot': str(TEST_INSTALL_ROOT)}).json()
    assert body['approved'] is True
    assert body['executed'][0]['status'] == 'executed'

