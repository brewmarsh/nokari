import firebase_admin
from firebase_admin import credentials, auth, firestore, storage

# Firebase Service Account Key (replace with secure storage in production)
# For demonstration purposes, embedding directly.
# In a real application, consider using environment variables or a secrets manager.
FIREBASE_SERVICE_ACCOUNT_KEY = {
  "type": "service_account",
  "project_id": "nokari-58e61",
  "private_key_id": "9c4553d485fe78fac4cbefddaf9d5528b6e8534b",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDDKCnvaj2eB//l\nBsC+wfvpKppuCQqSAbUzQj6O9j4wJ8CrzSn18Ksd4UzU8PlTaEDiNhRveIVKBwva\nPayFNrFCMBlYTmaP9I/br/Us2CHeiNQbVw64omIoCmioQ2swuMvSd/BKekp8b2cR\nHt7eqbyDPoHIu6YWsqRgYdfDfTi/s7wXRRWfoRxBsIKSL8T7RvP3aFF3Ywwu1QNl\nscOUrhSJB9SJRTcqjtWS2KVMb7xO0xbLF41jsgIgNDBFlCBpYoIPQLepEAoIVxEI\nCh5BTdJ/qOhmSZc71J+0ihARw1ZNx4kIqhS+K9Gf4UmntPHjFaYMkQd0HtzS0n3D\nsYEjL43hAgMBAAECggEAJUIlv2+pE+KzGCaR5dljHsDjet5/BiENVxvulZytgsQU\nJLimqi2ofavl30GiWCovOQDaJe38hIWT3baomUY30Usdi55sNk+ap3aQeF9LGBFH\nbXDRfq6BzuMt1/IHJOYjA6uiVJXEYr1iEAK0yg3dz7C/VnN84hh5CW2ko83kZ7Sz\nezELFC6HaYRdy4PnjI7wXFYkN8WDPJmJE9jRhgK63+49PLlg0lE+KCU7sDZvx38M\nuQdjS9Sf+P2jgaQlzEzghLZ4IneBwgkniXDoiwO6wx5UF3ynyAujU5LjS7eS1XHM\n9i2XcyNBEVTu8akzzZjHjXvCrXbCctOvQJuzyNPxgQKBgQDgdnHC+hO8xRXIaVOc\nFvIHaAuT8vydi5EZfFhcezoRMkreuokL54uAidjz8tvCySwsQ6y9OtjtdOndkfOm\nwvIdI33gEgIwUeGrUr872jiuLGc29ax1iXiBnNFHirohgp5Msw4p1E4rRGOTCnKK\nccj3Wd/na6DuVaI2MhLLhvH++wKBgQDek6NmLoWbOuPoUhLEYZR+/Tlfmx3b70e5\n16H30axNRN+4CdpWPBiZ6s/Rpc+OMDvH/YMdBlAAGAZNeoI0kRsEUMYuKL07Zluq\nuq9YVnaUJOl79dYbtTx1MCWn0cfDQjo1n7SEwrC29Y67D/+CeY25C6rm4f8+K4yN\n3Vg8ZG4f0wKBgDN/eUI+leCtZv4ADEq3iPfiCyX6jbKnnra2LJ+rNftUCpFnQqIU\nkZEAD2KIyZq7BQNy02Lm6XYxaKaJIdmUyG+fAPYzq4TihGAGMBHPU0nCrjuRyet9\nisRR8kHzthiSGzeFrS4zo2uR2TaXIwhYar81Q4WYz+dehkTg4CcJ4uOZAoGAIc8\nlW+knLFw2sFx/M0trRhrq8yXZ1EW1jHo/xSgZVydmIEuG2eCJECBF7x+TtpKHEir\nlFqyVzF3Z3z0DuD5ubyph4DMaA4LZ28Y9ylpf6sLsoILIQi82fsqQfbx07qkJtIm\nM3zm/pBsK0kls04HpUDmAfU/I+MWetRHxTEMpIzZAoGAZlXC4nrjhfCK/kmeVDCB\nk7NA5i43pwMwMxQ51cFHyG9Z19e4f4hlYyJQrN+7RvFLlpQywleL/oR+aowUl3v1\nwKLBC47jy8IS1Vr6yKO/BKcGEN/y2bgPnMNrUIq5R0yyBMknoxzXYcO+XKwKx656\n0KrChm+M/1Pn0JHL0+VL8kQ=\n-----END PRIVATE KEY-----\n".replace('\\n', '\n'),
  "client_email": "firebase-adminsdk-fbsvc@nokari-58e61.iam.gserviceaccount.com",
  "client_id": "112141848384381186710",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40nokari-58e61.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# Initialize Firebase Admin SDK
try:
    cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_KEY)
    firebase_admin.initialize_app(cred, {'storageBucket': f"{FIREBASE_SERVICE_ACCOUNT_KEY['project_id']}.appspot.com"})
    print("Firebase Admin SDK initialized successfully.")
except ValueError as e:
    print(f"Error initializing Firebase Admin SDK: {e}")
    # If the app is already initialized, we can ignore the error
    if "The default Firebase app already exists" not in str(e):
        raise

db = firestore.client()
firebase_auth = auth
firebase_storage = storage
