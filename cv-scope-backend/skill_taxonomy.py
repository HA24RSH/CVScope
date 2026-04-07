"""
skill_taxonomy.py
-----------------
Curated skill taxonomy: canonical_name → list of known aliases.
ALIAS_MAP provides O(1) lookup: any alias → canonical name.
PhraseMatcher patterns are built from this at startup.
"""

# Format: "canonical_name": ["alias1", "alias2", ...]
# Canonical is always lowercase, no punctuation except where part of the name (e.g. c++)
CANONICAL_SKILLS = {

    # ── Languages ────────────────────────────────────────────────────────────
    "python": ["python", "python3", "python 3"],
    "javascript": ["javascript", "js", "java script"],
    "typescript": ["typescript", "ts"],
    "java": ["java", "java se", "java ee", "j2ee"],
    "kotlin": ["kotlin"],
    "swift": ["swift", "swiftui"],
    "golang": ["go", "golang"],
    "rust": ["rust", "rust-lang", "rust lang"],
    "csharp": ["c#", "csharp", "c sharp"],
    "cpp": ["c++", "cpp", "c plus plus"],
    "c": ["c language", "c programming"],
    "ruby": ["ruby", "ruby on rails"],
    "php": ["php", "php7", "php8"],
    "scala": ["scala"],
    "perl": ["perl"],
    "r": ["r language", "r programming", "rlang"],
    "dart": ["dart"],
    "elixir": ["elixir"],
    "haskell": ["haskell"],
    "clojure": ["clojure"],
    "lua": ["lua"],
    "matlab": ["matlab"],
    "shell": ["shell", "bash", "bash scripting", "shell scripting", "sh"],
    "powershell": ["powershell", "pwsh"],

    # ── Frontend ─────────────────────────────────────────────────────────────
    "react": ["react", "reactjs", "react.js", "react js"],
    "react native": ["react native", "react-native"],
    "angular": ["angular", "angularjs", "angular.js", "angular js"],
    "vue": ["vue", "vuejs", "vue.js", "vue js"],
    "svelte": ["svelte", "sveltekit"],
    "nextjs": ["next.js", "nextjs", "next js"],
    "nuxtjs": ["nuxt.js", "nuxtjs", "nuxt js"],
    "html": ["html", "html5", "htm"],
    "css": ["css", "css3"],
    "sass": ["sass", "scss"],
    "tailwindcss": ["tailwind", "tailwindcss", "tailwind css"],
    "bootstrap": ["bootstrap"],
    "materialui": ["material ui", "material-ui", "mui"],
    "jquery": ["jquery"],
    "webpack": ["webpack"],
    "vite": ["vite"],
    "redux": ["redux", "redux toolkit", "rtk"],
    "graphql": ["graphql", "graph ql"],
    "webassembly": ["webassembly", "wasm"],
    "d3js": ["d3", "d3.js", "d3js"],
    "threejs": ["three.js", "threejs"],

    # ── Backend / Frameworks ──────────────────────────────────────────────────
    "nodejs": ["node", "node.js", "nodejs", "node js"],
    "express": ["express", "expressjs", "express.js", "express js"],
    "fastapi": ["fastapi", "fast api"],
    "django": ["django"],
    "flask": ["flask"],
    "spring": ["spring", "spring boot", "springboot"],
    "laravel": ["laravel"],
    "rails": ["rails", "ruby on rails"],
    "nestjs": ["nestjs", "nest.js", "nest js"],
    "gin": ["gin", "gin-gonic"],
    "fiber": ["fiber"],
    "actix": ["actix", "actix-web"],
    "aspnet": ["asp.net", "aspnet", "asp net", ".net core", "dotnet"],
    "fastify": ["fastify"],
    "hapi": ["hapi"],
    "tornado": ["tornado"],
    "aiohttp": ["aiohttp"],

    # ── Databases ─────────────────────────────────────────────────────────────
    "sql": ["sql"],
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres", "psql"],
    "sqlite": ["sqlite", "sqlite3"],
    "mongodb": ["mongodb", "mongo"],
    "redis": ["redis"],
    "firebase": ["firebase"],
    "elasticsearch": ["elasticsearch", "elastic search", "elk"],
    "cassandra": ["cassandra"],
    "dynamodb": ["dynamodb", "dynamo db"],
    "oracledb": ["oracle", "oracle db", "oracle database"],
    "mssql": ["mssql", "sql server", "microsoft sql server"],
    "neo4j": ["neo4j"],
    "couchdb": ["couchdb", "couch db"],
    "supabase": ["supabase"],
    "planetscale": ["planetscale"],
    "prisma": ["prisma"],
    "sqlalchemy": ["sqlalchemy"],
    "mongoose": ["mongoose"],
    "sequelize": ["sequelize"],

    # ── Cloud & DevOps ────────────────────────────────────────────────────────
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "terraform": ["terraform"],
    "ansible": ["ansible"],
    "jenkins": ["jenkins"],
    "github actions": ["github actions", "gh actions"],
    "gitlab ci": ["gitlab ci", "gitlab cicd", "gitlab pipelines"],
    "circleci": ["circleci", "circle ci"],
    "nginx": ["nginx"],
    "apache": ["apache", "apache httpd"],
    "linux": ["linux", "ubuntu", "debian", "centos"],
    "git": ["git"],
    "github": ["github"],
    "gitlab": ["gitlab"],
    "bitbucket": ["bitbucket"],
    "heroku": ["heroku"],
    "vercel": ["vercel"],
    "netlify": ["netlify"],
    "cloudflare": ["cloudflare"],
    "serverless": ["serverless", "lambda", "aws lambda"],

    # ── Data Science / ML / AI ────────────────────────────────────────────────
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"],
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch", "torch"],
    "keras": ["keras"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "numpy": ["numpy"],
    "pandas": ["pandas"],
    "matplotlib": ["matplotlib"],
    "seaborn": ["seaborn"],
    "opencv": ["opencv", "open cv", "cv2"],
    "nlp": ["nlp", "natural language processing"],
    "spacy": ["spacy", "spaCy"],
    "hugging face": ["hugging face", "huggingface", "transformers"],
    "langchain": ["langchain", "lang chain"],
    "openai": ["openai", "chatgpt api", "gpt"],
    "computer vision": ["computer vision"],
    "data analysis": ["data analysis", "data analytics"],
    "data visualization": ["data visualization", "data viz"],
    "tableau": ["tableau"],
    "power bi": ["power bi", "powerbi"],
    "hadoop": ["hadoop"],
    "spark": ["apache spark", "pyspark", "spark"],
    "kafka": ["kafka", "apache kafka"],
    "airflow": ["airflow", "apache airflow"],
    "mlflow": ["mlflow"],
    "jupyter": ["jupyter", "jupyter notebook", "jupyter lab"],

    # ── Mobile ────────────────────────────────────────────────────────────────
    "android": ["android", "android development"],
    "ios": ["ios", "ios development"],
    "flutter": ["flutter"],
    "xamarin": ["xamarin"],
    "ionic": ["ionic"],

    # ── Testing ───────────────────────────────────────────────────────────────
    "unit testing": ["unit testing", "unit tests"],
    "jest": ["jest"],
    "pytest": ["pytest"],
    "selenium": ["selenium"],
    "cypress": ["cypress"],
    "playwright": ["playwright"],
    "mocha": ["mocha"],
    "chai": ["chai"],
    "vitest": ["vitest"],
    "testng": ["testng"],
    "junit": ["junit"],

    # ── Architecture / Concepts ───────────────────────────────────────────────
    "rest api": ["rest", "rest api", "restful", "restful api"],
    "graphql api": ["graphql api"],
    "grpc": ["grpc", "rpc"],
    "microservices": ["microservices", "microservice architecture"],
    "event driven": ["event driven", "event-driven architecture"],
    "ci/cd": ["ci/cd", "cicd", "continuous integration", "continuous deployment"],
    "agile": ["agile", "scrum", "kanban"],
    "tdd": ["tdd", "test driven development"],
    "oop": ["oop", "object oriented programming", "object-oriented"],
    "functional programming": ["functional programming", "fp"],
    "system design": ["system design"],
    "design patterns": ["design patterns"],
    "api design": ["api design", "api development"],
    "websocket": ["websocket", "websockets", "ws"],
    "oauth": ["oauth", "oauth2", "jwt", "json web token"],

    # ── Blockchain ────────────────────────────────────────────────────────────
    "blockchain": ["blockchain", "web3", "web 3"],
    "solidity": ["solidity"],
    "ethereum": ["ethereum", "eth"],
    "smart contracts": ["smart contracts", "smart contract"],
    "nft": ["nft", "nfts"],

    # ── Security ─────────────────────────────────────────────────────────────
    "cybersecurity": ["cybersecurity", "cyber security", "infosec"],
    "penetration testing": ["penetration testing", "pentest", "pen testing"],
    "cryptography": ["cryptography"],
    "ssl/tls": ["ssl", "tls", "ssl/tls", "https"],

    # ── Tools ─────────────────────────────────────────────────────────────────
    "linux cli": ["cli", "command line", "terminal"],
    "postman": ["postman"],
    "figma": ["figma"],
    "jira": ["jira"],
    "confluence": ["confluence"],
    "notion": ["notion"],
    "vscode": ["vscode", "visual studio code", "vs code"],
    "vim": ["vim", "neovim", "nvim"],
    "wordpress": ["wordpress", "wp"],
    "shopify": ["shopify"],
    "excel": ["excel", "microsoft excel"],
    "google sheets": ["google sheets"],
    "zapier": ["zapier"],
}

# Flat alias map: any alias string → canonical skill name
# Used for O(1) lookup during normalization
ALIAS_MAP: dict[str, str] = {}
for canonical, aliases in CANONICAL_SKILLS.items():
    for alias in aliases:
        ALIAS_MAP[alias.lower()] = canonical

# All canonical skill names as a set (for quick membership check)
CANONICAL_SET: set[str] = set(CANONICAL_SKILLS.keys())
