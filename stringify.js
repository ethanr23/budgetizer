// https://forum.serverless.com/t/using-data-from-a-file-as-a-string-value-in-serverless-yml/10713/2

import { readFile } from 'fs/promises';

const googleCreds = async () => {
    const fileContents = await readFile('google-creds.json', 'utf-8')
        .then(data => JSON.parse(data))
        .catch(err => {
        console.error("Error reading google-creds.json:", err);
        throw err;
        });
    console.log("File contents:", fileContents);
    const stringified = JSON.stringify(fileContents);
    return stringified;
}

export default googleCreds;