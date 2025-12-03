// vscode-extension/extension.js
const vscode = require('vscode');
const axios = require('axios');

/**
 * Activates the extension.
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    let disposable = vscode.commands.registerCommand('aurora-proto.runAgent', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showInformationMessage('No active editor.');
            return;
        }

        const selection = editor.selection;
        const text = editor.document.getText(selection);

        // If no selection, use entire document
        const goal = text || editor.document.getText();

        vscode.window.showInformationMessage(`Running AURORA Agent on: ${goal.substring(0, 50)}...`);

        try {
            // Call local API (you need to run `python api_server.py` first)
            const response = await axios.post('http://localhost:5000/agent', {
                goal: goal
            });

            vscode.window.showInformationMessage('✅ AURORA Agent completed!');
            vscode.window.showInformationMessage(response.data.audit);

        } catch (error) {
            vscode.window.showErrorMessage(`❌ AURORA Agent failed: ${error.message}`);
        }
    });

    context.subscriptions.push(disposable);
}

exports.activate = activate;

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
