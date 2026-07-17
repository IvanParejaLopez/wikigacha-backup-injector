# WikiGacha Backup Injector Tool

A reverse-engineering and cryptographic data manipulation tool designed to inspect, decrypt, modify, and re-encrypt `.wgbak` backup files from the WikiGacha web game. This application bypasses manual data entry by allowing users to inject cards that was not in their collection in batches using an intuitive graphical user interface (GUI).

## Features
- **Cryptographic Core:** Implements full decryption and re-encryption pipelines utilizing PBKDF2 (SHA-256) key derivation and authenticated AES-256-GCM symmetric encryption.
- **Data Decompression:** Handles automated Gzip stream decompression and reconstruction to access the underlying game data.
- **Batch Card Injection:** Inject multiple card IDs and titles simultaneously without messing up the existing cryptographic signatures.
- **Duplicate Prevention:** Automatic ID filtering to prevent primary key collisions or overwriting your current collection.
- **Zero-Dependency Executable:** Packaged into a standalone `.exe` that runs out-of-the-box without requiring Python or external libraries.

---

## How It Works (The Synchronization Hack)
Wikigacha operates under a *Single Source of Truth* architecture. Instead of hardcoding all card details, the server validates existence based on legitimate Wikipedia **PageIDs**. 

By injecting a valid Wikipedia PageID and a temporary placeholder title into your local backup file, **the game's server acts as our automatic web scraper**. Upon importing, the game detects the legitimate ID, queries the Wikipedia database, and automatically populates the card with its real metadata, images, abstracts, and calculated stats.

---

## Step-by-Step Usage Guide

### 1. Export the Original Backup
1. Go to the official WikiGacha website and log in to your account.
2. Navigate to the **Collection** - **LOCAL BACKUP** section.
3. Click on **Export**.
<img width="2522" height="1182" alt="image" src="https://github.com/user-attachments/assets/6348163c-d367-4c3b-8d7c-688bc09a43f8" />

4. Set a security password (make sure to remember it) and download the generated `.wgbak` file.

### 2. Prepare the Cards You Want to Add
1. Go to the real, public [Wikipedia](https://en.wikipedia.org/) (or your respective language version).
2. Search for any article you want to turn into a card (e.g., "Cristiano Ronaldo", "Microsoft Windows").
3. On the top tools menu, click on **Page information**.
<img width="785" height="997" alt="image" src="https://github.com/user-attachments/assets/cf278424-1c21-4bea-ac25-2e26e44b360b" />

4. Locate the **Page ID** field under the basic technical information table. Copy this numerical ID.
<img width="473" height="473" alt="image" src="https://github.com/user-attachments/assets/bfbf3a45-1136-4bbe-bf60-7653fe3d86af" />


### 3. Inject the Cards Using the Tool
1. Download and run the `wikiCards.exe` from the **Releases** section of this repository.
2. Click on **Browse .wgbak file** and select the backup file you exported in Step 1.
3. Enter the exact **Password** you used when exporting the file.
4. In the **Add new card** section:
   - Paste the Wikipedia Page ID into the *Wikipedia ID* box.
   - Type a placeholder name into the *Título/Nombre* box.
   - Click **Add to list**. (Repeat this process for as many cards as you want).
5. Click the green button: **PROCESS AND INJECT BACKUP**.
6. Choose where to save your new modified backup file (e.g., `wikigacha_backup_modified.wgbak`).

### 4. Import Back to WikiGacha & Force Slicing
1. Go back to the official WikiGacha website.
2. Go to the same **Backup** section and select **Import**.
3. Upload your newly generated `wikigacha_backup_modificado.wgbak` file and type your password.
4. **Critical Step for Synchronization:** Your collection will load, but the injected cards will initially show temporary placeholder data. 
5. Go to your collection, search for the newly added cards by the temporary title you typed with the utility **Search by title**, and **click on them**.
<img width="2205" height="804" alt="image" src="https://github.com/user-attachments/assets/6603c80d-ac34-4651-8157-89b8a0813838" />

6. Opening the card forces the frontend JavaScript to fetch the official API endpoint. The screen will flash for a millisecond, and **the card will permanently update** with its real Wikipedia thumbnail illustration, full encyclopedic abstract, and accurate algorithmic combat stats.



###  **WARNING**
This is a way to explore cards if you were very curious about how a certain card would look like. However, this clearly is not the way the game is mean to be played and it takes all the fun out of it, so use it wisely ;)

---

## Technical Specifications
- **Language:** Python 3.12
- **Encryption Standards:** AES-GCM (256-bit key)
- **Key Derivation Function:** PBKDF2 with HMAC-SHA256 (210,000 iterations)
- **Payload Format:** Newline Delimited JSON (NDJSON) compressed via Gzip
- **GUI Framework:** Tkinter / TTK

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
