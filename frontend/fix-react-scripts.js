const fs = require('fs');
const path = require('path');

// Fix react-scripts webpack dev server config
const webpackConfigPath = path.join(__dirname, 'node_modules', 'react-scripts', 'config', 'webpackDevServer.config.js');

if (fs.existsSync(webpackConfigPath)) {
  let content = fs.readFileSync(webpackConfigPath, 'utf8');

  // Replace allowedHosts configuration
  if (content.includes('allowedHosts:')) {
    content = content.replace(
      /allowedHosts:\s*\[[\s\S]*?\],/,
      "allowedHosts: 'all',"
    );

    fs.writeFileSync(webpackConfigPath, content);
    console.log('✅ Fixed react-scripts webpack dev server config');
  } else {
    console.log('⚠️  Could not find allowedHosts in config');
  }
} else {
  console.log('⚠️  Webpack config file not found');
}
