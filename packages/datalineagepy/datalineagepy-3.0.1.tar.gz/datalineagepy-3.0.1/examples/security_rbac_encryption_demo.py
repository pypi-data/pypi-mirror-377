from datalineagepy.security.encryption.data_encryption import EncryptionManager
from datalineagepy.security.rbac import RBACManager
import os
# 32 chars for AES-256
os.environ['MASTER_ENCRYPTION_KEY'] = 'supersecretkey1234567890123456'

# RBAC Demo
rbac = RBACManager()
rbac.add_role('admin', ['read', 'write', 'delete'])
rbac.add_role('analyst', ['read'])
rbac.add_user('alice', ['admin'])
rbac.add_user('bob', ['analyst'])

print('Alice can write:', rbac.check_access('alice', 'write'))  # True
print('Bob can write:', rbac.check_access('bob', 'write'))      # False

# Encryption Demo
enc_mgr = EncryptionManager()
secret = "Sensitive DataLineagePy data!"
encrypted = enc_mgr.encrypt_sensitive_data(secret)
decrypted = enc_mgr.decrypt_sensitive_data(encrypted)

print('Original:', secret)
print('Encrypted:', encrypted)
print('Decrypted:', decrypted)
