"""
recommendations.py — CVScope Learning Resource Recommender
==========================================================
Maps canonical skill names → curated learning resources.
Each skill entry contains a list of resources with:
  - title  : human-readable name
  - url    : direct link
  - type   : "docs" | "video" | "course" | "roadmap" | "tutorial"
  - free   : bool (True = free resource)
"""

from __future__ import annotations

SKILL_RESOURCES: dict[str, list[dict]] = {
    # ── Languages ─────────────────────────────────────────────────────────────
    "python": [
        {"title": "Python Official Docs", "url": "https://docs.python.org/3/", "type": "docs", "free": True},
        {"title": "Python Full Course – freeCodeCamp", "url": "https://youtu.be/rfscVS0vtbw", "type": "video", "free": True},
        {"title": "roadmap.sh/python", "url": "https://roadmap.sh/python", "type": "roadmap", "free": True},
    ],
    "javascript": [
        {"title": "JavaScript MDN Docs", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript", "type": "docs", "free": True},
        {"title": "JavaScript Full Course – freeCodeCamp", "url": "https://youtu.be/jS4aFq5-91M", "type": "video", "free": True},
        {"title": "roadmap.sh/javascript", "url": "https://roadmap.sh/javascript", "type": "roadmap", "free": True},
    ],
    "typescript": [
        {"title": "TypeScript Official Docs", "url": "https://www.typescriptlang.org/docs/", "type": "docs", "free": True},
        {"title": "TypeScript Course – freeCodeCamp", "url": "https://youtu.be/SpwzRDUQ1GI", "type": "video", "free": True},
        {"title": "roadmap.sh/typescript", "url": "https://roadmap.sh/typescript", "type": "roadmap", "free": True},
    ],
    "java": [
        {"title": "Java Documentation – Oracle", "url": "https://docs.oracle.com/en/java/", "type": "docs", "free": True},
        {"title": "Java Full Course – Amigoscode", "url": "https://youtu.be/Qgl81fPcLc8", "type": "video", "free": True},
        {"title": "roadmap.sh/java", "url": "https://roadmap.sh/java", "type": "roadmap", "free": True},
    ],
    "kotlin": [
        {"title": "Kotlin Official Docs", "url": "https://kotlinlang.org/docs/home.html", "type": "docs", "free": True},
        {"title": "Kotlin Course – freeCodeCamp", "url": "https://youtu.be/F9UC9DY-vIU", "type": "video", "free": True},
    ],
    "golang": [
        {"title": "Go Official Docs", "url": "https://go.dev/doc/", "type": "docs", "free": True},
        {"title": "Go Tour (Interactive)", "url": "https://go.dev/tour/", "type": "tutorial", "free": True},
        {"title": "roadmap.sh/golang", "url": "https://roadmap.sh/golang", "type": "roadmap", "free": True},
    ],
    "rust": [
        {"title": "The Rust Book", "url": "https://doc.rust-lang.org/book/", "type": "docs", "free": True},
        {"title": "Rust Course – freeCodeCamp", "url": "https://youtu.be/BpPEoZW5IiY", "type": "video", "free": True},
        {"title": "roadmap.sh/rust", "url": "https://roadmap.sh/rust", "type": "roadmap", "free": True},
    ],
    "csharp": [
        {"title": "C# Documentation – Microsoft", "url": "https://learn.microsoft.com/en-us/dotnet/csharp/", "type": "docs", "free": True},
        {"title": "C# Full Course – freeCodeCamp", "url": "https://youtu.be/GhQdlIFylQ8", "type": "video", "free": True},
    ],
    "cpp": [
        {"title": "cppreference.com", "url": "https://en.cppreference.com/", "type": "docs", "free": True},
        {"title": "C++ Full Course – freeCodeCamp", "url": "https://youtu.be/8jLOx1hD3_o", "type": "video", "free": True},
    ],
    "ruby": [
        {"title": "Ruby Docs", "url": "https://ruby-doc.org/", "type": "docs", "free": True},
        {"title": "Ruby on Rails Guides", "url": "https://guides.rubyonrails.org/", "type": "docs", "free": True},
        {"title": "roadmap.sh/ruby", "url": "https://roadmap.sh/ruby", "type": "roadmap", "free": True},
    ],
    "php": [
        {"title": "PHP Manual", "url": "https://www.php.net/manual/en/", "type": "docs", "free": True},
        {"title": "PHP Full Course – freeCodeCamp", "url": "https://youtu.be/OK_JCtrrv-c", "type": "video", "free": True},
        {"title": "roadmap.sh/php", "url": "https://roadmap.sh/php", "type": "roadmap", "free": True},
    ],
    "shell": [
        {"title": "Bash Scripting Tutorial", "url": "https://linuxconfig.org/bash-scripting-tutorial", "type": "tutorial", "free": True},
        {"title": "Shell Scripting – freeCodeCamp", "url": "https://youtu.be/v-F3YLd6oMw", "type": "video", "free": True},
    ],

    # ── Frontend ──────────────────────────────────────────────────────────────
    "react": [
        {"title": "React Official Docs", "url": "https://react.dev/", "type": "docs", "free": True},
        {"title": "React Full Course – freeCodeCamp", "url": "https://youtu.be/bMknfKXIFA8", "type": "video", "free": True},
        {"title": "roadmap.sh/react", "url": "https://roadmap.sh/react", "type": "roadmap", "free": True},
    ],
    "nextjs": [
        {"title": "Next.js Official Docs", "url": "https://nextjs.org/docs", "type": "docs", "free": True},
        {"title": "Next.js Full Course – freeCodeCamp", "url": "https://youtu.be/843nec-IvW0", "type": "video", "free": True},
        {"title": "roadmap.sh/nextjs", "url": "https://roadmap.sh/nextjs", "type": "roadmap", "free": True},
    ],
    "vue": [
        {"title": "Vue Official Docs", "url": "https://vuejs.org/guide/", "type": "docs", "free": True},
        {"title": "Vue.js Full Course – freeCodeCamp", "url": "https://youtu.be/FXpIoQ_rT_c", "type": "video", "free": True},
        {"title": "roadmap.sh/vue", "url": "https://roadmap.sh/vue", "type": "roadmap", "free": True},
    ],
    "angular": [
        {"title": "Angular Official Docs", "url": "https://angular.io/docs", "type": "docs", "free": True},
        {"title": "Angular Full Course – freeCodeCamp", "url": "https://youtu.be/3qBXWUpoPHo", "type": "video", "free": True},
        {"title": "roadmap.sh/angular", "url": "https://roadmap.sh/angular", "type": "roadmap", "free": True},
    ],
    "svelte": [
        {"title": "Svelte Official Tutorial", "url": "https://learn.svelte.dev/", "type": "tutorial", "free": True},
        {"title": "Svelte Crash Course – Traversy Media", "url": "https://youtu.be/3TVy6GdtNuQ", "type": "video", "free": True},
    ],
    "html": [
        {"title": "HTML MDN Docs", "url": "https://developer.mozilla.org/en-US/docs/Web/HTML", "type": "docs", "free": True},
        {"title": "HTML Full Course – freeCodeCamp", "url": "https://youtu.be/pQN-pnXPaVg", "type": "video", "free": True},
    ],
    "css": [
        {"title": "CSS MDN Docs", "url": "https://developer.mozilla.org/en-US/docs/Web/CSS", "type": "docs", "free": True},
        {"title": "CSS Full Course – freeCodeCamp", "url": "https://youtu.be/OXGznpKZ_sA", "type": "video", "free": True},
    ],
    "tailwindcss": [
        {"title": "Tailwind CSS Docs", "url": "https://tailwindcss.com/docs", "type": "docs", "free": True},
        {"title": "Tailwind CSS Full Course – freeCodeCamp", "url": "https://youtu.be/ft30zcMlFa8", "type": "video", "free": True},
    ],
    "redux": [
        {"title": "Redux Toolkit Docs", "url": "https://redux-toolkit.js.org/", "type": "docs", "free": True},
        {"title": "Redux Full Course – freeCodeCamp", "url": "https://youtu.be/zrs7u6bdbUw", "type": "video", "free": True},
    ],
    "graphql": [
        {"title": "GraphQL Official Docs", "url": "https://graphql.org/learn/", "type": "docs", "free": True},
        {"title": "GraphQL Full Course – freeCodeCamp", "url": "https://youtu.be/ed8SzALpx1Q", "type": "video", "free": True},
    ],

    # ── Backend ───────────────────────────────────────────────────────────────
    "nodejs": [
        {"title": "Node.js Official Docs", "url": "https://nodejs.org/en/docs/", "type": "docs", "free": True},
        {"title": "Node.js Full Course – freeCodeCamp", "url": "https://youtu.be/Oe421EPjeBE", "type": "video", "free": True},
        {"title": "roadmap.sh/nodejs", "url": "https://roadmap.sh/nodejs", "type": "roadmap", "free": True},
    ],
    "express": [
        {"title": "Express.js Official Docs", "url": "https://expressjs.com/", "type": "docs", "free": True},
        {"title": "Express.js Course – freeCodeCamp", "url": "https://youtu.be/SccSCuHhOw0", "type": "video", "free": True},
    ],
    "fastapi": [
        {"title": "FastAPI Official Docs", "url": "https://fastapi.tiangolo.com/", "type": "docs", "free": True},
        {"title": "FastAPI Crash Course – freeCodeCamp", "url": "https://youtu.be/0sOvCWFmrtA", "type": "video", "free": True},
    ],
    "django": [
        {"title": "Django Official Docs", "url": "https://docs.djangoproject.com/", "type": "docs", "free": True},
        {"title": "Django Full Course – freeCodeCamp", "url": "https://youtu.be/F5mRW0jo-U4", "type": "video", "free": True},
        {"title": "roadmap.sh/django", "url": "https://roadmap.sh/django", "type": "roadmap", "free": True},
    ],
    "flask": [
        {"title": "Flask Official Docs", "url": "https://flask.palletsprojects.com/", "type": "docs", "free": True},
        {"title": "Flask Full Course – freeCodeCamp", "url": "https://youtu.be/Qr4QMBUPxWo", "type": "video", "free": True},
    ],
    "spring": [
        {"title": "Spring Framework Docs", "url": "https://spring.io/guides", "type": "docs", "free": True},
        {"title": "Spring Boot Full Course – Amigoscode", "url": "https://youtu.be/9SGDpanrc8U", "type": "video", "free": True},
        {"title": "roadmap.sh/spring-boot", "url": "https://roadmap.sh/spring-boot", "type": "roadmap", "free": True},
    ],

    # ── Databases ─────────────────────────────────────────────────────────────
    "sql": [
        {"title": "SQLZoo (Interactive SQL)", "url": "https://sqlzoo.net/", "type": "tutorial", "free": True},
        {"title": "SQL Full Course – freeCodeCamp", "url": "https://youtu.be/HXV3zeQKqGY", "type": "video", "free": True},
        {"title": "roadmap.sh/sql", "url": "https://roadmap.sh/sql", "type": "roadmap", "free": True},
    ],
    "postgresql": [
        {"title": "PostgreSQL Official Docs", "url": "https://www.postgresql.org/docs/", "type": "docs", "free": True},
        {"title": "PostgreSQL Full Course – freeCodeCamp", "url": "https://youtu.be/qw--VYLpxG4", "type": "video", "free": True},
    ],
    "mysql": [
        {"title": "MySQL Official Docs", "url": "https://dev.mysql.com/doc/", "type": "docs", "free": True},
        {"title": "MySQL Full Course – freeCodeCamp", "url": "https://youtu.be/7S_tz1z_5bA", "type": "video", "free": True},
    ],
    "mongodb": [
        {"title": "MongoDB Official Docs", "url": "https://www.mongodb.com/docs/", "type": "docs", "free": True},
        {"title": "MongoDB Full Course – freeCodeCamp", "url": "https://youtu.be/ofme2o29ngU", "type": "video", "free": True},
        {"title": "MongoDB University (Free)", "url": "https://learn.mongodb.com/", "type": "course", "free": True},
    ],
    "redis": [
        {"title": "Redis Documentation", "url": "https://redis.io/docs/", "type": "docs", "free": True},
        {"title": "Redis Crash Course – Traversy Media", "url": "https://youtu.be/jgpVdJB2sKQ", "type": "video", "free": True},
    ],
    "firebase": [
        {"title": "Firebase Official Docs", "url": "https://firebase.google.com/docs", "type": "docs", "free": True},
        {"title": "Firebase Full Course – freeCodeCamp", "url": "https://youtu.be/9kRgVxULbag", "type": "video", "free": True},
    ],
    "prisma": [
        {"title": "Prisma Official Docs", "url": "https://www.prisma.io/docs", "type": "docs", "free": True},
        {"title": "Prisma Crash Course", "url": "https://youtu.be/RebA5J-rlwg", "type": "video", "free": True},
    ],

    # ── Cloud & DevOps ────────────────────────────────────────────────────────
    "aws": [
        {"title": "AWS Documentation", "url": "https://docs.aws.amazon.com/", "type": "docs", "free": True},
        {"title": "AWS Full Course – freeCodeCamp", "url": "https://youtu.be/ulprqHHWlng", "type": "video", "free": True},
        {"title": "roadmap.sh/aws", "url": "https://roadmap.sh/aws", "type": "roadmap", "free": True},
    ],
    "docker": [
        {"title": "Docker Official Docs", "url": "https://docs.docker.com/", "type": "docs", "free": True},
        {"title": "Docker Full Course – freeCodeCamp", "url": "https://youtu.be/fqMOX6JJhGo", "type": "video", "free": True},
        {"title": "roadmap.sh/docker", "url": "https://roadmap.sh/docker", "type": "roadmap", "free": True},
    ],
    "kubernetes": [
        {"title": "Kubernetes Official Docs", "url": "https://kubernetes.io/docs/", "type": "docs", "free": True},
        {"title": "Kubernetes Full Course – freeCodeCamp", "url": "https://youtu.be/d6WC5n9G_sM", "type": "video", "free": True},
        {"title": "roadmap.sh/kubernetes", "url": "https://roadmap.sh/kubernetes", "type": "roadmap", "free": True},
    ],
    "terraform": [
        {"title": "Terraform Official Docs", "url": "https://developer.hashicorp.com/terraform/docs", "type": "docs", "free": True},
        {"title": "Terraform Full Course – freeCodeCamp", "url": "https://youtu.be/SLB_c_ayRMo", "type": "video", "free": True},
    ],
    "git": [
        {"title": "Git Official Docs", "url": "https://git-scm.com/doc", "type": "docs", "free": True},
        {"title": "Git & GitHub Full Course – freeCodeCamp", "url": "https://youtu.be/RGOj5yH7evk", "type": "video", "free": True},
        {"title": "roadmap.sh/git-github", "url": "https://roadmap.sh/git-github", "type": "roadmap", "free": True},
    ],
    "github actions": [
        {"title": "GitHub Actions Docs", "url": "https://docs.github.com/en/actions", "type": "docs", "free": True},
        {"title": "GitHub Actions Full Course", "url": "https://youtu.be/R8_veQiYBjI", "type": "video", "free": True},
    ],
    "ci/cd": [
        {"title": "CI/CD Overview – Atlassian", "url": "https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment", "type": "docs", "free": True},
        {"title": "CI/CD Pipeline Tutorial – freeCodeCamp", "url": "https://youtu.be/1hHMwLxN6EM", "type": "video", "free": True},
        {"title": "roadmap.sh/devops", "url": "https://roadmap.sh/devops", "type": "roadmap", "free": True},
    ],
    "linux": [
        {"title": "Linux Command Line – freeCodeCamp", "url": "https://youtu.be/rowTL9sOmzA", "type": "video", "free": True},
        {"title": "roadmap.sh/linux", "url": "https://roadmap.sh/linux", "type": "roadmap", "free": True},
    ],
    "azure": [
        {"title": "Azure Docs – Microsoft Learn", "url": "https://learn.microsoft.com/en-us/azure/", "type": "docs", "free": True},
        {"title": "Azure Full Course – freeCodeCamp", "url": "https://youtu.be/NKEFWyqJ5XA", "type": "video", "free": True},
    ],
    "gcp": [
        {"title": "Google Cloud Docs", "url": "https://cloud.google.com/docs", "type": "docs", "free": True},
        {"title": "Google Cloud Skills Boost (Free Tier)", "url": "https://cloudskillsboost.google/", "type": "course", "free": True},
    ],

    # ── ML / AI ───────────────────────────────────────────────────────────────
    "machine learning": [
        {"title": "ML Crash Course – Google", "url": "https://developers.google.com/machine-learning/crash-course", "type": "course", "free": True},
        {"title": "Machine Learning Specialization – Coursera", "url": "https://www.coursera.org/specializations/machine-learning-introduction", "type": "course", "free": False},
        {"title": "roadmap.sh/ai-data-scientist", "url": "https://roadmap.sh/ai-data-scientist", "type": "roadmap", "free": True},
    ],
    "deep learning": [
        {"title": "Deep Learning Specialization – Coursera", "url": "https://www.coursera.org/specializations/deep-learning", "type": "course", "free": False},
        {"title": "Deep Learning – freeCodeCamp", "url": "https://youtu.be/VyWAvY2CF9c", "type": "video", "free": True},
    ],
    "tensorflow": [
        {"title": "TensorFlow Official Docs", "url": "https://www.tensorflow.org/learn", "type": "docs", "free": True},
        {"title": "TensorFlow Full Course – freeCodeCamp", "url": "https://youtu.be/tPYj3fFJGjk", "type": "video", "free": True},
    ],
    "pytorch": [
        {"title": "PyTorch Official Tutorials", "url": "https://pytorch.org/tutorials/", "type": "docs", "free": True},
        {"title": "PyTorch Full Course – freeCodeCamp", "url": "https://youtu.be/V_xro1bcAuA", "type": "video", "free": True},
    ],
    "scikit-learn": [
        {"title": "scikit-learn Docs", "url": "https://scikit-learn.org/stable/user_guide.html", "type": "docs", "free": True},
        {"title": "scikit-learn Crash Course", "url": "https://youtu.be/0B5eIE_1vpU", "type": "video", "free": True},
    ],

    # ── Architecture / Concepts ───────────────────────────────────────────────
    "rest api": [
        {"title": "RESTful API Design – Best Practices", "url": "https://restfulapi.net/", "type": "docs", "free": True},
        {"title": "REST API Tutorial – freeCodeCamp", "url": "https://youtu.be/0sOvCWFmrtA", "type": "video", "free": True},
        {"title": "roadmap.sh/api-design", "url": "https://roadmap.sh/api-design", "type": "roadmap", "free": True},
    ],
    "microservices": [
        {"title": "Microservices Guide – Martin Fowler", "url": "https://martinfowler.com/articles/microservices.html", "type": "docs", "free": True},
        {"title": "Microservices Full Course – freeCodeCamp", "url": "https://youtu.be/lTAcCNbJ7KE", "type": "video", "free": True},
        {"title": "roadmap.sh/microservices", "url": "https://roadmap.sh/microservices", "type": "roadmap", "free": True},
    ],
    "system design": [
        {"title": "System Design Primer – GitHub", "url": "https://github.com/donnemartin/system-design-primer", "type": "docs", "free": True},
        {"title": "System Design Full Course – freeCodeCamp", "url": "https://youtu.be/F2FmTdLtb_4", "type": "video", "free": True},
        {"title": "roadmap.sh/system-design", "url": "https://roadmap.sh/system-design", "type": "roadmap", "free": True},
    ],
    "agile": [
        {"title": "Agile Manifesto", "url": "https://agilemanifesto.org/", "type": "docs", "free": True},
        {"title": "Scrum Guide", "url": "https://scrumguides.org/", "type": "docs", "free": True},
    ],

    # ── Mobile ────────────────────────────────────────────────────────────────
    "flutter": [
        {"title": "Flutter Official Docs", "url": "https://docs.flutter.dev/", "type": "docs", "free": True},
        {"title": "Flutter Full Course – freeCodeCamp", "url": "https://youtu.be/VPvVD8t02U8", "type": "video", "free": True},
        {"title": "roadmap.sh/flutter", "url": "https://roadmap.sh/flutter", "type": "roadmap", "free": True},
    ],
    "react native": [
        {"title": "React Native Official Docs", "url": "https://reactnative.dev/docs/getting-started", "type": "docs", "free": True},
        {"title": "React Native Full Course – freeCodeCamp", "url": "https://youtu.be/obH0Po_RdWk", "type": "video", "free": True},
        {"title": "roadmap.sh/react-native", "url": "https://roadmap.sh/react-native", "type": "roadmap", "free": True},
    ],

    # ── Testing ───────────────────────────────────────────────────────────────
    "jest": [
        {"title": "Jest Official Docs", "url": "https://jestjs.io/docs/getting-started", "type": "docs", "free": True},
        {"title": "Jest Crash Course – Traversy Media", "url": "https://youtu.be/7r4xVDI2vho", "type": "video", "free": True},
    ],
    "pytest": [
        {"title": "Pytest Official Docs", "url": "https://docs.pytest.org/", "type": "docs", "free": True},
        {"title": "Pytest Full Course", "url": "https://youtu.be/cHYq1MRoyI0", "type": "video", "free": True},
    ],
    "cypress": [
        {"title": "Cypress Official Docs", "url": "https://docs.cypress.io/", "type": "docs", "free": True},
        {"title": "Cypress Full Course – freeCodeCamp", "url": "https://youtu.be/u8vMu7viCm8", "type": "video", "free": True},
    ],

    # ── Security ──────────────────────────────────────────────────────────────
    "cybersecurity": [
        {"title": "roadmap.sh/cyber-security", "url": "https://roadmap.sh/cyber-security", "type": "roadmap", "free": True},
        {"title": "Cybersecurity Full Course – freeCodeCamp", "url": "https://youtu.be/U_P23SqJaDc", "type": "video", "free": True},
    ],

    # ── Web3 ──────────────────────────────────────────────────────────────────
    "blockchain": [
        {"title": "roadmap.sh/blockchain", "url": "https://roadmap.sh/blockchain", "type": "roadmap", "free": True},
        {"title": "Blockchain Full Course – freeCodeCamp", "url": "https://youtu.be/gyMwXuJrbJQ", "type": "video", "free": True},
    ],
    "solidity": [
        {"title": "Solidity Official Docs", "url": "https://docs.soliditylang.org/", "type": "docs", "free": True},
        {"title": "Solidity Full Course – freeCodeCamp", "url": "https://youtu.be/M576WGiDBdQ", "type": "video", "free": True},
    ],

    # ── Tools ─────────────────────────────────────────────────────────────────
    "figma": [
        {"title": "Figma Official Docs", "url": "https://help.figma.com/", "type": "docs", "free": True},
        {"title": "Figma Full Course – freeCodeCamp", "url": "https://youtu.be/jwCmIBJ8Jtc", "type": "video", "free": True},
    ],
    "postman": [
        {"title": "Postman Learning Center", "url": "https://learning.postman.com/", "type": "docs", "free": True},
        {"title": "Postman Course – freeCodeCamp", "url": "https://youtu.be/VywxIQ2ZXw4", "type": "video", "free": True},
    ],
}

# Fallback for skills not in the curated list
_GENERIC_FALLBACK = [
    {"title": "Search on YouTube", "url": "https://www.youtube.com/results?search_query={skill}+tutorial", "type": "video", "free": True},
    {"title": "Search on freeCodeCamp", "url": "https://www.freecodecamp.org/news/search/?query={skill}", "type": "tutorial", "free": True},
    {"title": "roadmap.sh", "url": "https://roadmap.sh/", "type": "roadmap", "free": True},
]


def get_recommendations(missing_skills: list[str]) -> list[dict]:
    """
    Return a list of recommendation objects for each missing skill.
    Each object: {"skill": str, "resources": list[dict]}

    Resources are sorted: docs/roadmap first, then video, then course.
    Falls back to generic search links for unknown skills.
    """
    order = {"roadmap": 0, "docs": 1, "tutorial": 2, "video": 3, "course": 4}
    result = []
    for skill in missing_skills:
        resources = SKILL_RESOURCES.get(skill)
        if resources:
            sorted_resources = sorted(resources, key=lambda r: order.get(r["type"], 99))
        else:
            sorted_resources = [
                {
                    "title": r["title"],
                    "url": r["url"].replace("{skill}", skill.replace(" ", "+")),
                    "type": r["type"],
                    "free": r["free"],
                }
                for r in _GENERIC_FALLBACK
            ]
        result.append({"skill": skill, "resources": sorted_resources[:3]})
    return result
