from __future__ import annotations

from app.services.release_service import stage_local_artifacts
from pathlib import Path
from app.services.store import (
    save_auth_tokens,
    save_entitlements,
    save_install_receipts,
    save_install_scans,
    save_release_manifests,
    save_seats,
    save_settings,
    save_webhooks,
)

DEMO_ENTITLEMENTS = {
    'demo_account': {
        'accountId': 'demo_account',
        'ownsEveryVST': True,
        'ownedProducts': [],
        'ownedBundles': ['complete_collection'],
        'extraSeatQuantity': 2,
        'billingState': 'active',
    },
    'free_account': {
        'accountId': 'free_account',
        'ownsEveryVST': False,
        'ownedProducts': [],
        'ownedBundles': [],
        'extraSeatQuantity': 0,
        'billingState': 'active',
    },
}

DEMO_RELEASES = {
    'freeeq8': {'productId': 'freeeq8', 'channel': 'stable', 'latestVersion': '1.0.0', 'artifactMode': 'source', 'artifactUrl': 'https://github.com/GareBear99/FreeEQ8', 'sha256': 'sha256_freeeq8_demo_1000', 'signature': 'arc-demo-signed', 'notes': 'Open repo build available.'},
    'therum': {'productId': 'therum', 'channel': 'stable', 'latestVersion': '1.0.0', 'artifactMode': 'source', 'artifactUrl': 'https://github.com/GareBear99/Therum', 'sha256': 'sha256_therum_demo_1000', 'signature': 'arc-demo-signed', 'notes': 'Flagship synth scaffold.'},
    'wurp': {'productId': 'wurp', 'channel': 'beta', 'latestVersion': '0.8.5', 'artifactMode': 'source', 'artifactUrl': 'https://github.com/GareBear99/WURP', 'sha256': 'sha256_wurp_demo_0850', 'signature': 'arc-demo-signed', 'notes': 'Beta channel track for Toxicron branch.'},
    'aether': {'productId': 'aether', 'channel': 'stable', 'latestVersion': '0.8.2', 'artifactMode': 'source', 'artifactUrl': 'https://github.com/GareBear99/AETHER', 'sha256': 'sha256_aether_demo_0820', 'signature': 'arc-demo-signed', 'notes': 'Addon-capable atmosphere designer scaffold.'},
    'whispergate': {'productId': 'whispergate', 'channel': 'stable', 'latestVersion': '0.7.5', 'artifactMode': 'source', 'artifactUrl': 'https://github.com/GareBear99/WhisperGate', 'sha256': 'sha256_whispergate_demo_0750', 'signature': 'arc-demo-signed', 'notes': 'Free ritual atmosphere scaffold.'},
    'paintmask': {'productId': 'paintmask', 'channel': 'stable', 'latestVersion': '0.6.0', 'artifactMode': 'source', 'artifactUrl': 'https://github.com/GareBear99/PaintMask', 'sha256': 'sha256_paintmask_demo_0600', 'signature': 'arc-demo-signed', 'notes': 'Studio package scaffold, source-distributed.'},
    'waveform_riftsynth_lite': {'productId': 'waveform_riftsynth_lite', 'channel': 'stable', 'latestVersion': '1.0.0', 'artifactMode': 'source', 'artifactUrl': 'https://github.com/GareBear99/WaveForm-RiftSynth-Lite', 'sha256': 'sha256_waveformlite_demo_1000', 'signature': 'arc-demo-signed', 'notes': 'Free lite combo release.'},
    'waveform_pro': {'productId': 'waveform_pro', 'channel': 'stable', 'latestVersion': '0.9.1', 'artifactMode': 'source', 'artifactUrl': 'https://github.com/GareBear99/WaveForm-Pro', 'sha256': 'sha256_waveformpro_demo_0910', 'signature': 'arc-demo-signed', 'notes': 'Pro build plan placeholder.'},
    'riftsynth_pro': {'productId': 'riftsynth_pro', 'channel': 'stable', 'latestVersion': '0.9.1', 'artifactMode': 'source', 'artifactUrl': 'https://github.com/GareBear99/RiftSynth-Pro', 'sha256': 'sha256_riftsynthpro_demo_0910', 'signature': 'arc-demo-signed', 'notes': 'Pro build plan placeholder.'},
}


def bootstrap_demo_state(stage_artifacts: bool = True) -> dict:
    save_entitlements(DEMO_ENTITLEMENTS)
    save_seats({})
    save_install_scans([])
    save_install_receipts([])
    save_webhooks([])
    save_auth_tokens({})
    save_release_manifests(DEMO_RELEASES)
    if LOCAL_AUTH_DB.exists():
        LOCAL_AUTH_DB.unlink()

    save_settings({
        'demo_account': {
            'machineId': 'mac_demo',
            'preferredChannel': 'stable',
            'theme': 'dark',
            'arcBaseUrl': 'http://127.0.0.1:8000',
            'installRoot': '/tmp/tizhub_installs',
            'autoStageOnBootstrap': True,
            'autoBackupBeforeExecute': True,
        },
        'free_account': {
            'machineId': 'mac_free',
            'preferredChannel': 'stable',
            'theme': 'light',
            'arcBaseUrl': 'http://127.0.0.1:8000',
            'installRoot': '/tmp/tizhub_installs',
            'autoStageOnBootstrap': True,
            'autoBackupBeforeExecute': False,
        },
    })

    staged = {}
    if stage_artifacts:
        staged.update(stage_local_artifacts('stable'))
        staged.update(stage_local_artifacts('beta'))

    return {
        'approved': True,
        'message': 'demo_bootstrap_complete',
        'accounts': sorted(DEMO_ENTITLEMENTS.keys()),
        'releaseCount': len(DEMO_RELEASES),
        'stagedCount': len(staged),
        'stagedProducts': sorted(staged.keys()),
    }


LOCAL_AUTH_DB = Path(__file__).resolve().parent.parent / "data" / "arc_local_auth.sqlite3"
