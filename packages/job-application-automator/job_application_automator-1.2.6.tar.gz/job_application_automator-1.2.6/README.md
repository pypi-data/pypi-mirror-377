# Job Application Automator

🤖 **Automated job application form extraction and filling with Claude Desktop integration via Model Context Protocol (MCP).**

Streamline your job search by automating form data extraction and filling while maintaining full control over submissions.

## 🚀 Quick Start

**Simple 2-step process for any user:**

```bash
# Step 1: Install from PyPI
pip install job-application-automator

# Step 2: Setup Claude Desktop
job-automator-setup
```

**That's it! Users get:**
- ✅ All dependencies automatically installed
- ✅ Playwright browsers configured
- ✅ Claude Desktop MCP integration set up
- ✅ Cross-platform Unicode compatibility
- ✅ Professional package distribution

**Restart Claude Desktop** and you're ready to go!

## 📋 Prerequisites

- **Python 3.10+** - [Download here](https://python.org/downloads/)
- **Node.js & npm** - [Download here](https://nodejs.org/) (for enhanced features)
- **Claude Desktop** - [Download here](https://claude.ai/desktop)

## 🚀 Alternative Installation Methods

### Option 1: From PyPI (Recommended)
```bash
pip install job-application-automator
job-automator-setup
```

### Option 2: From Git Repository
```bash
git clone https://github.com/username/job-application-automator.git
cd job-application-automator
python scripts/quick_setup.py
```

### Option 3: Direct Install
```bash
pip install git+https://github.com/username/job-application-automator.git
job-automator-setup
```

## ✨ Features

- **🔍 Form Extraction**: Automatically extract form fields from any job posting URL
- **📝 Intelligent Form Filling**: Fill forms with your information while keeping browser open for review
- **💼 Cover Letter Generation**: Create personalized cover letters for each application  
- **📊 Applied Jobs Tracking**: Beautiful dashboard showing all your job applications
- **🔒 Privacy First**: All processing happens locally on your machine
- **🛡️ Stealth Mode**: Uses undetected browser automation to avoid bot detection
- **🎯 Claude Desktop Integration**: Seamless MCP integration with Claude Desktop

## 💡 Usage

After installation, interact with Claude Desktop using natural language:

### Extract Form Data
```
Extract form fields from https://company.com/careers/software-engineer
```

### Fill Job Application
```
Fill the job application form with my information:
- Name: John Doe
- Email: john@example.com
- Phone: +1-555-0123
- Resume: /path/to/resume.pdf
```

### View Application History
```
Show me my applied jobs dashboard
```

### Generate Cover Letter
```
Create a cover letter for the Software Engineer position at TechCorp
```

## 🛠️ What's Included

### MCP Tools Available in Claude Desktop:

1. **`simple_form_extraction`**
   - Extracts form structure from job posting URLs
   - Identifies required fields, field types, and form layout
   - Handles complex forms (Greenhouse, Workday, etc.)

2. **`simple_form_filling`** 
   - Fills forms with your provided information
   - Opens browser for manual review before submission
   - Supports file uploads (resume, cover letter)

3. **`create_cover_letter`**
   - Generates personalized cover letters
   - Saves with timestamp and company info
   - Customizable templates

4. **`get_applied_jobs`**
   - Shows beautiful dashboard of all applications
   - Tracks application dates and statuses
   - Export capabilities

5. **`health_check`**
   - Monitor server status
   - Check browser automation health
   - Debug connection issues

## 🔧 Manual Setup

If you prefer manual configuration:

### 1. Install Package
```bash
pip install job-application-automator
```

### 2. Configure Claude Desktop

Add to your Claude Desktop config file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Linux**: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "job-automator": {
      "command": "job-automator-mcp"
    }
  }
}
```

### 3. Install Browser Dependencies
```bash
playwright install chromium
```

### 4. Restart Claude Desktop

## 📋 System Requirements

- **Python**: 3.10 or higher
- **Operating System**: Windows, macOS, or Linux  
- **Claude Desktop**: Latest version
- **Memory**: 4GB+ RAM recommended
- **Storage**: 500MB for dependencies

## 🔒 Privacy & Security

- **Local Processing**: All form data stays on your machine
- **No Data Collection**: Nothing is sent to external services  
- **Manual Control**: You review every form before submission
- **Stealth Browsing**: Avoids website bot detection
- **Secure Storage**: Temporary files are automatically cleaned up

## 🏗️ Architecture

```
Claude Desktop ←→ MCP Server ←→ Form Modules ←→ Browser Automation
     ↑                ↑              ↑              ↑
  User Chat      FastMCP        Extractor/      Playwright
               Protocol       Filler Logic    (Undetected)
```

**How it works:**
1. You ask Claude to extract or fill a form
2. Claude calls the appropriate MCP tool
3. MCP server delegates to form automation modules  
4. Browser automation handles the web interaction
5. Results are returned to you through Claude

## 🚀 Example Workflow

1. **Find Job Posting**
   ```
   "Extract form data from https://greenhouse.io/company/job/apply"
   ```

2. **Review Extracted Fields**
   Claude shows you all the form fields that were found

3. **Fill Application**
   ```
   "Fill the form with my information:
   Name: Jane Smith
   Email: jane@example.com
   Phone: +1-555-0123
   Resume: C:\Documents\resume.pdf"
   ```

4. **Review & Submit**
   Browser opens with form pre-filled - you review and submit manually

5. **Track Application**
   ```
   "Show my job applications dashboard"
   ```

## 🛠️ Development

### Local Development Setup
```bash
git clone https://github.com/jobautomator/job-application-automator
cd job-application-automator
pip install -e .
job-automator-setup
```

## 🧪 Installation Verification

Check if everything is working:

```bash
# Check prerequisites
python scripts/check_prerequisites.py

# Test package installation
python -c "import job_application_automator; print('✅ Package installed')"

# Test MCP server
python job_application_automator/mcp_server.py
```

### Troubleshooting

If you encounter issues:

1. **Check prerequisites**: `python scripts/check_prerequisites.py`
2. **Verify Claude config**: See `examples/claude_config_example.json`
3. **Manual setup**: Follow detailed instructions in [INSTALL.md](INSTALL.md)
4. **Get help**: Check [GitHub Issues](https://github.com/username/job-application-automator/issues)

## 🗂️ Repository Structure

```
job-application-automator/
├── .github/workflows/       # CI/CD workflows
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── INSTALL.md              # Detailed installation guide
├── LICENSE                 # MIT License
├── pyproject.toml          # Package configuration
├── requirements.txt        # Python dependencies
├── job_application_automator/  # Main package
│   ├── __init__.py
│   ├── mcp_server.py       # FastMCP server
│   ├── form_extractor.py   # Form extraction engine
│   ├── form_filler.py      # Form filling automation
│   ├── setup_claude.py     # Claude Desktop setup
│   └── mcp_config/         # MCP configuration
├── scripts/                # Installation scripts
│   ├── quick_setup.py      # Cross-platform setup
│   ├── install.sh          # Linux/macOS setup
│   ├── install.bat         # Windows setup
│   └── check_prerequisites.py  # Requirements check
└── examples/               # Example files
    ├── claude_config_example.json
    ├── sample_form_data.json
    └── README.md
```

### Run Tests
```bash
python -m pytest tests/ -v
```

### Development Setup
```bash
git clone https://github.com/username/job-application-automator.git
cd job-application-automator
pip install -e .
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Areas We Need Help With:
- Additional job board integrations
- UI/UX improvements for the dashboard
- Performance optimizations
- Documentation improvements
- Test coverage expansion

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/jobautomator/job-application-automator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jobautomator/job-application-automator/discussions)
- **Email**: contact@jobautomator.dev

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- [Playwright](https://playwright.dev/) for browser automation
- [Undetected Playwright](https://github.com/kaliiiiiiiiii/undetected-playwright) for stealth automation
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) for MCP server framework

## 📈 Roadmap

- [ ] **v1.1**: GUI application for non-technical users
- [ ] **v1.2**: Integration with more job boards (Indeed, LinkedIn, etc.)
- [ ] **v1.3**: AI-powered application optimization suggestions
- [ ] **v1.4**: Team collaboration features
- [ ] **v1.5**: Mobile app support

---

**Made with ❤️ for job seekers everywhere**

*Automate the tedious, focus on what matters - landing your dream job!*
