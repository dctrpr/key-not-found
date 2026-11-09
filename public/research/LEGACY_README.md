# Max Keiser Bitcoin Puzzle Decoder & Solver

This tool helps decode the hidden message in the text and automatically checks for valid Bitcoin private keys (Mnemonics or WIFs).

## How to use

1. **Start the Server**:
   The server should be running automatically. If not, run:
   ```bash
   node server.js
   ```

2. **Open the Decoder**:
   - Open your web browser and go to: **[http://localhost:3000](http://localhost:3000)**
   
3. **Input Data**:
   - **Puzzle Text**: Paste the text from the PDF (preserve line breaks!).
   - **Bolded Content**: 
     - Look at the **PDF** file.
     - Type the full bolded words into the "Bolded Words" box.
     - Type the individual bolded letters into the "Bolded Letters" box.

4. **Run Automation**:
   - Click **"RUN AUTOMATED SOLVER"**.
   - The tool will generate thousands of candidates based on strategies (George Sand, Mirror, etc.) and check them against the Bitcoin blockchain for activity.
   - Valid keys with funds will appear in the "Results" section.

## Troubleshooting

- If the server stops, check the terminal for errors.
- Rate limits: The tool automatically pauses if it hits API rate limits.
