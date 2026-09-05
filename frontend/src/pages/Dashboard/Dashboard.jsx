import { useEffect, useState } from "react";

import {
  getGithubMe,
  syncGithubActivity,
  getGithubActivity,
  getGithubActivities,
  getWorkSummary,
} from "../../api/github";

import { generatePost } from "../../api/posts";

import {
  Bell,
  Settings,
  ChevronDown,
  CalendarDays,
  Activity,
  Folder,
  Code2,
  GitBranch,
  Sparkles,
  Copy,
  RefreshCw,
  ExternalLink,
  Clock3,
  Check,
} from "lucide-react";

import black_logo from "../../assets/black_logo_logs.png";

import "./Dashboard.css";

const Dashboard = () => {

  const [github, setGithub] = useState(null);
  const [githubActivity, setGithubActivity] = useState(null);
  const [activities, setActivities] = useState([]);
  const [summary, setSummary] = useState(null);

  const [workSummaryId, setWorkSummaryId] = useState(null);



  const [platform, setPlatform] = useState("x");
  const [postLength, setPostLength] = useState(500);
  const [style, setStyle] = useState("Casual & authentic");
  const [inspiration, setInspiration] = useState("");
  const [excludedTopics, setExcludedTopics] = useState([]);



  const [generatedPost, setGeneratedPost] = useState("");

  
  // UI STATES
  

  const [dashboardLoading, setDashboardLoading] = useState(true);
  const [postLoading, setPostLoading] = useState(false);

  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  
  // POST TIME
  

  const getCurrentTime = () => {
    const now = new Date();

    return `${String(now.getHours()).padStart(2, "0")}:${String(
      now.getMinutes(),
    ).padStart(2, "0")}`;
  };

  const [postTime, setPostTime] = useState(getCurrentTime());

  
  // LOAD DASHBOARD AUTOMATICALLY
  

  async function loadDashboard(time = postTime) {
    try {
      setDashboardLoading(true);
      setError("");

      // 1. GitHub profile
      const githubData = await getGithubMe();

      setGithub(githubData);

      // 2. Sync GitHub events into Activities table
      await syncGithubActivity(time);

      // 3. Fetch raw GitHub window information
      const githubActivityData = await getGithubActivity(time);

      setGithubActivity(githubActivityData);

      // 4. Retrieve saved normalized activities
      const activitiesData = await getGithubActivities(time);

      setActivities(Array.isArray(activitiesData) ? activitiesData : []);

      // 5. Generate/retrieve LLM work summary
      const summaryData = await getWorkSummary(time);

      setSummary(summaryData.llm_summary);

      /*
        IMPORTANT:

        Your current backend response showed:

        {
          "llm_summary": ...
        }

        but your generate_post endpoint requires work_summary_id.

        If you change retrieve_summary_llm to also return:

        {
          "work_summary_id": db_worksummary.id,
          "llm_summary": llm_summary
        }

        this will work:
      */

      if (summaryData.work_summary_id) {
        setWorkSummaryId(summaryData.work_summary_id);
      }
    } catch (err) {
      console.error("Dashboard loading failed:", err);

      if (err.response) {
        setError(err.response.data?.detail || "Could not load today's work.");
      } else {
        setError("Could not connect to LOGS backend.");
      }
    } finally {
      setDashboardLoading(false);
    }
  }

  
  // AUTOMATIC FIRST LOAD
  

  useEffect(() => {
    loadDashboard();
  }, []);

  
  // GENERATE POST
  

  async function handleGeneratePost() {
    if (!workSummaryId) {
      setError(
        "Work summary ID is missing. The summary endpoint needs to return it.",
      );

      return;
    }

    try {
      setPostLoading(true);
      setError("");

      const data = await generatePost(
        workSummaryId,
        platform,
        postLength,
        style,
        inspiration,
        excludedTopics,
      );


      let post = data.post;

      if (typeof post === "object" && post !== null) {
        post = post.post;
      }

      if (typeof post === "string" && post.trim().startsWith("{")) {
        try {
          const parsed = JSON.parse(post);

          if (parsed.post) {
            post = parsed.post;
          }
        } catch {
        }
      }

      setGeneratedPost(post || "");
    } catch (err) {
      console.error("Post generation failed:", err);

      setError(err.response?.data?.detail || "Could not generate your post.");
    } finally {
      setPostLoading(false);
    }
  }

    

  async function handleCopy() {
    if (!generatedPost) return;

    try {
      await navigator.clipboard.writeText(generatedPost);

      setCopied(true);

      setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch (err) {
      console.error("Clipboard failed:", err);
    }
  }

  

  

  function openPlatform() {
    const urls = {
      x: "https://x.com/compose/post",
      linkedin: "https://www.linkedin.com/feed/",
      reddit: "https://www.reddit.com/submit",
      devto: "https://dev.to/new",
    };

    const url = urls[platform];

    if (url) {
      window.open(url, "_blank", "noopener,noreferrer");
    }
  }

  
  

  const projects = Array.isArray(summary?.projects) ? summary.projects : [];

  const technologies = Array.isArray(summary?.technologies)
    ? summary.technologies
    : [];

  const accomplishments = Array.isArray(summary?.accomplishments)
    ? summary.accomplishments
    : [];

  const problemsSolved = Array.isArray(summary?.problems_solved)
    ? summary.problems_solved
    : [];

  
  

  if (dashboardLoading) {
    return (
      <div className="dashboard-loading">
        <img src={black_logo} alt="LOGS" />

        <h2>LOGS is remembering what you built...</h2>

        <p>Looking through today's GitHub activity.</p>
      </div>
    );
  }


  

  return (
    <div className="dashboard">
    

      <header className="dashboard-nav">
        <div className="brand">
          <img src={black_logo} alt="LOGS" />
          <span>LOGS</span>
        </div>

        <nav>
          <button className="nav-active">Overview</button>

          <button>History</button>
        </nav>

        <div className="nav-right">
          <Bell size={20} />

          <Settings size={20} />

          {github && (
            <div className="profile">
              {github.avatar_url && (
                <img src={github.avatar_url} alt={github.username} />
              )}

              <span>{github.username}</span>

              <ChevronDown size={16} />
            </div>
          )}
        </div>
      </header>

      {/* =====================================
          PAGE INTRO
      ====================================== */}

      <section className="dashboard-intro">
        <div>
          <p className="greeting">Good evening,</p>

          <h1>{github?.username || "Builder"} 👋</h1>

          <p className="intro-description">
            Here's what you've been building today. LOGS analyzed your GitHub
            activity and prepared a summary.
          </p>
        </div>

        <div className="dashboard-status">
          <div className="updated-status">
            <span className="status-dot" />
            Updated just now
          </div>

          <div className="posting-time">
            <Clock3 size={18} />

            <div>
              <span>Posting time</span>

              <input
                type="time"
                value={postTime}
                onChange={(e) => setPostTime(e.target.value)}
              />
            </div>

            <button
              onClick={() => loadDashboard(postTime)}
              title="Refresh using this posting time"
            >
              <RefreshCw size={16} />
            </button>
          </div>
        </div>
      </section>

      {error && <div className="dashboard-error">{error}</div>}

      {/* =====================================
          MAIN GRID
      ====================================== */}

      <main className="dashboard-layout">
        {/* LEFT SIDE */}

        <div className="dashboard-left">
          {/* TODAY'S WORK */}

          <section className="today-card">
            <div className="today-card-header">
              <div className="card-title">
                <CalendarDays size={19} />

                <h2>Today's Work</h2>
              </div>

              <span>
                {new Date().toLocaleDateString(undefined, {
                  weekday: "short",
                  month: "short",
                  day: "numeric",
                  year: "numeric",
                })}
              </span>
            </div>

            <h1>Built, learned and made progress.</h1>

            <p className="work-summary">
              {summary?.summary || "No work summary available yet."}
            </p>

            {/* STATS */}

            <div className="stats-grid">
              <div className="stat-card">
                <Activity />

                <strong>{activities.length}</strong>

                <span>Activities</span>
              </div>

              <div className="stat-card">
                <Folder />

                <strong>{projects.length}</strong>

                <span>Projects</span>
              </div>

              <div className="stat-card">
                <Code2 />

                <strong>{technologies.length}</strong>

                <span>Technologies</span>
              </div>

              <div className="stat-card">
                <GitBranch />

                <strong>{githubActivity?.count ?? 0}</strong>

                <span>GitHub Events</span>
              </div>
            </div>

            {/* HIGHLIGHTS */}

            <div className="work-details">
              <div>
                <h3>Top highlights</h3>

                {accomplishments.map((item, index) => (
                  <div className="highlight" key={index}>
                    <span className="highlight-dot" />

                    {typeof item === "string" ? item : item.description}
                  </div>
                ))}
              </div>

              <div>
                <h3>Technologies used</h3>

                <div className="technology-tags">
                  {technologies.map((technology, index) => (
                    <span key={index}>
                      {typeof technology === "string"
                        ? technology
                        : technology.name}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </section>

          {/* LOWER GRID */}

          <div className="dashboard-bottom-grid">
            {/* RECENT ACTIVITY */}

            <section className="dashboard-card">
              <h2>Recent Activity</h2>

              <div className="recent-list">
                {activities.slice(0, 5).map((activity, index) => (
                  <div className="recent-item" key={activity.id || index}>
                    <div className="recent-icon">
                      <GitBranch size={16} />
                    </div>

                    <span>
                      {activity.description ||
                        activity.title ||
                        activity.activity_type ||
                        "GitHub activity"}
                    </span>
                  </div>
                ))}
              </div>
            </section>

            {/* PROJECTS */}

            <section className="dashboard-card">
              <h2>Projects</h2>

              <div className="project-list">
                {projects.map((project, index) => (
                  <div className="project-item" key={index}>
                    <Folder size={19} />

                    <span>
                      {typeof project === "string" ? project : project.name}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          </div>

          {/* PROBLEMS SOLVED */}

          {problemsSolved.length > 0 && (
            <section className="dashboard-card problems-card">
              <h2>Problems Solved</h2>

              {problemsSolved.map((problem, index) => (
                <div className="problem-item" key={index}>
                  {typeof problem === "string" ? problem : problem.description}
                </div>
              ))}
            </section>
          )}
        </div>

        {/* =====================================
            RIGHT SIDE — POST CREATOR
        ====================================== */}

        <aside className="post-panel">
          <div className="post-panel-title">
            <Sparkles size={25} />

            <div>
              <h2>Generate a Post</h2>

              <p>Turn today's work into something worth sharing.</p>
            </div>
          </div>

          {/* PLATFORM */}

          <div className="form-group">
            <label>Platform</label>

            <div className="platform-options">
              {[
                ["x", "𝕏"],
                ["linkedin", "LinkedIn"],
                ["reddit", "Reddit"],
                ["devto", "Dev.to"],
              ].map(([value, label]) => (
                <button
                  key={value}
                  className={platform === value ? "selected" : ""}
                  onClick={() => setPlatform(value)}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* LENGTH */}

          <div className="form-group">
            <label>Length</label>

            <div className="length-options">
              <button
                className={postLength === 280 ? "selected" : ""}
                onClick={() => setPostLength(280)}
              >
                Short
              </button>

              <button
                className={postLength === 500 ? "selected" : ""}
                onClick={() => setPostLength(500)}
              >
                Medium
              </button>

              <button
                className={postLength === 1200 ? "selected" : ""}
                onClick={() => setPostLength(1200)}
              >
                Long
              </button>
            </div>
          </div>

          {/* STYLE */}

          <div className="form-group">
            <label>Style</label>

            <select value={style} onChange={(e) => setStyle(e.target.value)}>
              <option>Casual & authentic</option>

              <option>Technical deep dive</option>

              <option>Builder update</option>

              <option>Crazy student style</option>

              <option>Professional</option>
            </select>
          </div>

          {/* INSPIRATION */}

          <div className="form-group">
            <label>
              Inspiration
              <span> optional</span>
            </label>

            <textarea
              value={inspiration}
              onChange={(e) => setInspiration(e.target.value)}
              placeholder="Paste a post or describe the vibe you want..."
            />
          </div>

          {/* EXCLUDED TOPICS */}

          <div className="form-group">
            <label>
              Exclude topics
              <span> optional</span>
            </label>

            <input
              type="text"
              placeholder="Personal info, certain technologies..."
              onChange={(e) => {
                const topics = e.target.value
                  .split(",")
                  .map((topic) => topic.trim())
                  .filter(Boolean);

                setExcludedTopics(topics);
              }}
            />
          </div>

          {/* GENERATE */}

          <button
            className="generate-button"
            onClick={handleGeneratePost}
            disabled={postLoading}
          >
            <Sparkles size={18} />

            {postLoading ? "Writing..." : "Generate post"}
          </button>

          {/* GENERATED POST */}

          {generatedPost && (
            <div className="generated-post">
              <div className="generated-post-header">
                <h3>Your Post</h3>

                <button onClick={handleGeneratePost} disabled={postLoading}>
                  <RefreshCw size={15} />
                  Regenerate
                </button>
              </div>

              <textarea
                className="post-editor"
                value={generatedPost}
                onChange={(e) => setGeneratedPost(e.target.value)}
              />

              <div className="post-actions">
                <button className="copy-button" onClick={handleCopy}>
                  {copied ? <Check size={17} /> : <Copy size={17} />}

                  {copied ? "Copied!" : "Copy to clipboard"}
                </button>

                <button className="platform-open-button" onClick={openPlatform}>
                  <ExternalLink size={17} />
                  Open{" "}
                  {platform === "x"
                    ? "X"
                    : platform === "linkedin"
                      ? "LinkedIn"
                      : platform === "reddit"
                        ? "Reddit"
                        : "Dev.to"}
                </button>
              </div>
            </div>
          )}
        </aside>
      </main>
    </div>
  );
};

export default Dashboard;
