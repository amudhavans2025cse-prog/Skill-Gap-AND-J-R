import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import axios from 'axios';
import {
  Activity, ArrowUpRight, BarChart3, Bell, BookOpen, BriefcaseBusiness, Check, CheckCircle2,
  ChevronDown, ChevronRight, Clock3, Compass, FileText, GraduationCap, House, LoaderCircle,
  LogOut, MapPin, MapPinned, Menu, Pencil, Plus, Search, Settings2, ShieldAlert, Sparkles,
  Target, UploadCloud, UserRound, X, BrainCircuit,
} from 'lucide-react';
import './dashboard.css';

const API = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '') + '/api';
const DEMO_SKILLS = ['Python', 'SQL', 'Git', 'HTML', 'CSS'];
const DEMO_PROFILE = {
  name: 'Arun Kumar', email: 'student@example.com', phone: '',
  education: 'B.Tech Computer Science', degree: 'B.Tech', graduation_year: '2026',
  experience: 'Student', location: 'Bengaluru, India',
  preferred_job_role: 'Machine Learning Engineer', preferred_location: 'Bengaluru, India',
  certifications: [],
};
const NAV_ITEMS = [
  { label: 'Dashboard', href: '#dashboard', icon: House },
  { label: 'Profile', href: '#profile-card', icon: UserRound },
  { label: 'Resume Analyzer', href: '#resume-analyzer', icon: FileText },
  { label: 'My Skills', href: '#my-skills', icon: Settings2 },
  { label: 'Skill Gap', href: '#skill-gap', icon: Target },
  { label: 'Recommended Jobs', href: '#recommended-jobs', icon: BriefcaseBusiness },
  { label: 'Career Roadmap', href: '#career-roadmap', icon: MapPinned },
  { label: 'Courses', href: '#recommended-courses', icon: BookOpen },
  { label: 'Progress', href: '#career-progress', icon: BarChart3 },
];

function App() {
  const [skills, setSkills] = useState(DEMO_SKILLS);
  const [catalog, setCatalog] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [selected, setSelected] = useState('');
  const [gap, setGap] = useState(null);
  const [roadmap, setRoadmap] = useState(null);
  const [courses, setCourses] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [newSkill, setNewSkill] = useState('');
  const [token, setToken] = useState(() => localStorage.getItem('skillgap_token') || '');
  const [authMode, setAuthMode] = useState('');
  const [profileOpen, setProfileOpen] = useState(false);
  const [navOpen, setNavOpen] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [searchFilter, setSearchFilter] = useState('');
  const [authForm, setAuthForm] = useState({ name: '', email: '', password: '' });
  const [profile, setProfile] = useState(DEMO_PROFILE);

  const loadDashboard = async (jobId, activeSkills) => {
    if (!jobId) return;
    setLoading('analysis');
    try {
      const [analysis, plan, ranked, courseResponse] = await Promise.all([
        axios.post(`${API}/analyze`, { skills: activeSkills, job_id: jobId }),
        axios.post(`${API}/roadmap`, { skills: activeSkills, job_id: jobId }),
        axios.post(`${API}/recommend`, {
          skills: activeSkills, education: profile.education, experience: profile.experience,
          preferred_job_role: profile.preferred_job_role, preferred_location: profile.preferred_location,
        }),
        axios.get(`${API}/courses/recommended`, { params: { skills: activeSkills } }),
      ]);
      const missing = new Set(analysis.data.missing_skills.map((skill) => skill.toLowerCase()));
      setGap(analysis.data);
      setRoadmap(plan.data);
      setRecommendations(ranked.data.recommendations);
      setCourses(courseResponse.data.courses.filter((course) => missing.has(course.skill.toLowerCase())));
      setError('');
    } catch {
      setError('Could not load your career analysis. Check the API connection and try again.');
    } finally {
      setLoading('');
    }
  };

  useEffect(() => {
    let active = true;
    Promise.all([axios.get(`${API}/jobs`), axios.get(`${API}/skills`)])
      .then(([jobResponse, skillResponse]) => {
        if (!active) return;
        const availableJobs = jobResponse.data.jobs;
        setJobs(availableJobs);
        setCatalog(skillResponse.data.skills);
        const target = availableJobs.find((job) => job.title === 'Machine Learning Engineer') || availableJobs[0];
        if (target) {
          setSelected(target.job_id);
          loadDashboard(target.job_id, DEMO_SKILLS);
        }
      })
      .catch(() => setError('Could not connect to the API. Start the FastAPI backend and try again.'));
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!token) return;
    axios.get(`${API}/profile`, { headers: { Authorization: `Bearer ${token}` } })
      .then(({ data }) => {
        setProfile((current) => ({ ...current, ...data.profile }));
        if (data.profile.skills?.length) setSkills(data.profile.skills);
      })
      .catch(() => {
        localStorage.removeItem('skillgap_token');
        setToken('');
        setError('Your saved profile could not be loaded. Sign in again or continue in demo mode.');
      });
  }, [token]);

  const jumpTo = (selector) => {
    setNavOpen(false);
    document.querySelector(selector)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const submitAuth = async (event) => {
    event.preventDefault();
    setLoading('auth');
    setError('');
    try {
      const payload = authMode === 'register' ? authForm : { email: authForm.email, password: authForm.password };
      const { data } = await axios.post(`${API}/auth/${authMode}`, payload);
      localStorage.setItem('skillgap_token', data.access_token);
      setToken(data.access_token);
      setAuthMode('');
      setAuthForm({ name: '', email: '', password: '' });
      setMessage('Signed in. Your profile is ready to edit.');
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Sign in failed. Check your connection and account details.');
    } finally {
      setLoading('');
    }
  };

  const saveProfile = async (event) => {
    event.preventDefault();
    if (token) {
      setLoading('profile');
      try {
        await axios.put(`${API}/profile`, {
          ...profile, graduation_year: profile.graduation_year ? Number(profile.graduation_year) : null, skills,
        }, { headers: { Authorization: `Bearer ${token}` } });
      } catch (requestError) {
        setError(requestError.response?.data?.detail || 'Could not save your profile.');
        setLoading('');
        return;
      }
      setLoading('');
    }
    setProfileOpen(false);
    setMessage(token ? 'Profile saved. Your job matches use these preferences.' : 'Profile updated for this demo session.');
    if (selected) loadDashboard(selected, skills);
  };

  const logout = () => {
    localStorage.removeItem('skillgap_token');
    setToken('');
    setProfile(DEMO_PROFILE);
    setMessage('Signed out. Demo mode is still available.');
  };

  const refreshRecommendations = async () => {
    setLoading('recommendations');
    try {
      const { data } = await axios.post(`${API}/recommend`, {
        skills, education: profile.education, experience: profile.experience,
        preferred_job_role: profile.preferred_job_role, preferred_location: profile.preferred_location,
      });
      setRecommendations(data.recommendations);
      setError('');
    } catch {
      setError('Could not load recommendations. Check the API connection and try again.');
    } finally {
      setLoading('');
    }
  };

  const toggleSkill = (skill) => {
    setSkills((current) => current.includes(skill) ? current.filter((value) => value !== skill) : [...current, skill]);
    setGap(null);
    setRoadmap(null);
    setCourses([]);
    setRecommendations([]);
  };

  const addSkill = (event) => {
    event.preventDefault();
    const value = newSkill.trim();
    if (value && !skills.some((existing) => existing.toLowerCase() === value.toLowerCase())) setSkills((current) => [...current, value]);
    setNewSkill('');
    setGap(null);
    setRoadmap(null);
    setCourses([]);
    setRecommendations([]);
  };

  const uploadResume = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setLoading('resume');
    setError('');
    setMessage('');
    const form = new FormData();
    form.append('file', file);
    try {
      const { data } = await axios.post(`${API}/resume/upload`, form);
      const extracted = data.skills;
      setSkills((current) => [...current, ...extracted.filter((skill) => !current.some((value) => value.toLowerCase() === skill.toLowerCase()))]);
      setGap(null);
      setRoadmap(null);
      setCourses([]);
      setRecommendations([]);
      setMessage(extracted.length ? `Resume analysis completed. Found ${extracted.length} catalog skills.` : 'No catalog skills found. Add skills manually to continue.');
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Resume upload failed. Use a readable PDF, DOCX, or TXT file up to 5 MB.');
    } finally {
      setLoading('');
      event.target.value = '';
    }
  };

  const applySearch = (event) => {
    event.preventDefault();
    setSearchFilter(searchText.trim().toLowerCase());
    jumpTo('#recommended-jobs');
    if (!recommendations.length) refreshRecommendations();
  };

  const selectedJob = jobs.find((job) => job.job_id === selected);
  const matched = gap?.matched_skills || [];
  const missing = gap?.missing_skills || [];
  const score = gap?.match_percentage || 0;
  const profileScore = Math.round([profile.name, profile.email, profile.education, profile.graduation_year, profile.preferred_job_role, profile.preferred_location, skills.length > 0].filter(Boolean).length / 7 * 100);
  const filteredJobs = recommendations.filter((job) => !searchFilter || `${job.title} ${job.company} ${job.location} ${job.required_skills.join(' ')}`.toLowerCase().includes(searchFilter));
  const jumpToJobs = () => { setSearchFilter(''); jumpTo('#all-jobs'); };

  return (
    <div className="workspace">
      {navOpen && <button className="mobile-scrim" aria-label="Close navigation" onClick={() => setNavOpen(false)} />}
      <aside className={`sidebar ${navOpen ? 'sidebar-open' : ''}`} style={navOpen ? { transform: 'translateX(0)' } : undefined}>
        <button className="brand-lockup" onClick={() => jumpTo('#dashboard')}><span className="brand-mark"><BrainCircuit size={27} /></span><span><strong>SkillBridge</strong><small>AI Skill Gap & Job Recommendation System</small></span></button>
        <nav className="side-nav" aria-label="Main navigation">{NAV_ITEMS.map(({ label, href, icon: Icon }, index) => <button className={`side-link ${index === 0 ? 'active' : ''}`} key={label} onClick={() => jumpTo(href)}><Icon size={17} /><span>{label}</span></button>)}</nav>
        <button className="side-link side-logout" onClick={token ? logout : () => setAuthMode('login')}><LogOut size={17} /><span>{token ? 'Logout' : 'Sign in'}</span></button>
        <div className="sidebar-callout"><div className="callout-art"><Compass size={22} /><ArrowUpRight size={14} /></div><strong>Your Future<br />Your Skills<br />Our AI</strong><span>Build your career with smart guidance.</span></div>
        <span className="sidebar-foot">SIH · Career readiness</span>
      </aside>

      <div className="main-shell">
        <header className="topbar">
          <button className="mobile-menu icon-control" aria-label="Open navigation" onClick={() => setNavOpen(true)}><Menu size={19} /></button>
          <form className="global-search" onSubmit={applySearch}><Search size={17} /><input aria-label="Search jobs, skills, or courses" placeholder="Search for jobs, skills, or courses..." value={searchText} onChange={(event) => setSearchText(event.target.value)} /><button type="submit" aria-label="Search"><Search size={16} /></button></form>
          <button className="notification icon-control" aria-label="Notifications" onClick={() => setMessage('You are all caught up on career updates.')}><Bell size={19} /><i /></button>
          <button className="user-menu" onClick={() => token ? setProfileOpen(true) : setAuthMode('login')}><img src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=96&q=80" alt="" /><span><strong>{profile.name}</strong><small>{token ? 'Student account' : 'Student'}</small></span><ChevronDown size={14} /></button>
        </header>

        <main className="dashboard" id="dashboard">
          {(error || message) && <div className={`toast ${error ? 'toast-error' : ''}`} role="status"><span>{error || message}</span><button aria-label="Dismiss message" onClick={() => { setError(''); setMessage(''); }}><X size={15} /></button></div>}
          <section className="hero-row">
            <div className="hero-banner"><img className="hero-image" src="https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1200&q=85" alt="Students planning their future together" /><div className="hero-shade" />
              <div className="hero-copy"><span className="hero-kicker"><Sparkles size={14} />AI-powered career guidance</span><h1>Bridge the Gap Between Your Skills and Your <em>Dream Career</em></h1><p>AI-powered skill analysis, personalized job recommendations, and career roadmaps for students and job seekers.</p>
                <div className="hero-actions"><button className="button-primary" onClick={() => { jumpTo('#target-role'); if (selected) loadDashboard(selected, skills); }}><UploadCloud size={16} />Analyze My Skills</button><button className="button-secondary" onClick={() => jumpTo('#recommended-jobs')}><Search size={16} />Explore Jobs</button></div>
              </div><span className="hero-label label-learn">Learn</span><span className="hero-label label-improve">Improve</span><span className="hero-label label-grow">Grow</span>
            </div>
            <section className="profile-card" id="profile-card"><div className="profile-heading"><img src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=120&q=80" alt="" /><div><strong>{profile.name}</strong><span>{profile.email}</span><b><CheckCircle2 size={13} />Profile {profileScore}% Complete</b></div></div>
              <div className="profile-detail"><GraduationCap size={14} /><span>{profile.education || 'Add your education'}</span></div><div className="profile-detail"><UserRound size={14} /><span>Target Role: {profile.preferred_job_role || 'Choose a role'}</span></div><div className="profile-detail"><MapPin size={14} /><span>Location: {profile.location || 'Add your location'}</span></div><button className="profile-edit" onClick={() => token ? setProfileOpen(true) : setAuthMode('register')}><Pencil size={13} />Edit Profile</button>
            </section>
          </section>

          <section className="stat-grid" aria-label="Career summary"><StatCard icon={UserRound} label="Profile Score" value={`${profileScore}%`} color="blue" foot={`${skills.length} skills in your profile`} progress={profileScore} /><StatCard icon={Settings2} label="Current Skills" value={skills.length} color="green" foot="Skills ready to match" /><StatCard icon={BriefcaseBusiness} label="Recommended Jobs" value={recommendations.length || jobs.length} color="blue" foot={`${jobs.length} roles in the catalog`} /><StatCard icon={ShieldAlert} label="Skill Gaps" value={missing.length} color="coral" foot={selectedJob ? `For ${selectedJob.title}` : 'Select a target role'} /></section>

          <section className="dashboard-grid dashboard-top-grid">
            <section className="widget skill-widget" id="skills-overview"><WidgetHeading title="Your Skill Overview" action="View All" onAction={() => jumpTo('#my-skills')} />
              {gap?.required_skills?.length ? <div className="skill-chart-list">{gap.required_skills.map((skill, index) => { const hasSkill = matched.some((item) => item.toLowerCase() === skill.toLowerCase()); return <div className="skill-chart-row" key={skill}><span className={`skill-icon skill-icon-${index % 5}`}>{skill === 'Machine Learning' ? 'ML' : skill.slice(0, 1)}</span><span className="skill-name">{skill}</span><span className="skill-track"><i className={hasSkill ? 'matched-fill' : 'missing-fill'} style={{ width: hasSkill ? '100%' : '8%' }} /></span><strong>{hasSkill ? 'Matched' : 'Gap'}</strong></div>; })}</div> : <EmptyState text="Choose a target role to compare your skills." />}
              <button className="text-action" onClick={() => jumpTo('#my-skills')}>Manage skills <ChevronRight size={14} /></button>
            </section>

            <section className="widget jobs-widget" id="recommended-jobs"><WidgetHeading title="Top Job Recommendations" action="View All" onAction={jumpToJobs} /><div className="job-list">{filteredJobs.slice(0, 4).map((job, index) => <JobRow key={job.job_id} job={job} index={index} />)}{!filteredJobs.length && <EmptyState text={searchFilter ? 'No recommended jobs match that search.' : 'Loading your job matches...'} />}</div><button className="text-action" disabled={loading === 'recommendations'} onClick={refreshRecommendations}>{loading === 'recommendations' ? 'Refreshing...' : 'Refresh matches'} <ArrowUpRight size={14} /></button></section>

            <section className="widget gap-widget" id="skill-gap"><WidgetHeading title="Skill Gap Analysis" action="View All" onAction={() => jumpTo('#target-role')} /><div className="gap-chart-area"><div className="donut" style={{ '--match-angle': `${score * 3.6}deg` }}><div className="donut-center"><strong>{Math.round(score)}%</strong><span>Match Score</span></div></div><div className="gap-legend"><span><i className="legend-dot matched-dot" />Matched Skills <b>{matched.length}</b></span><span><i className="legend-dot missing-dot" />Missing Skills <b>{missing.length}</b></span><span><i className="legend-dot optional-dot" />Required Skills <b>{gap?.required_skills?.length || 0}</b></span></div></div><div className="gap-tip">{missing.length ? <>Build <strong>{missing.length} skills</strong> to improve your match for {selectedJob?.title || 'this role'}.</> : 'Run an analysis to calculate your match.'}</div></section>
          </section>

          <section className="dashboard-grid dashboard-bottom-grid">
            <section className="widget progress-widget" id="career-progress"><WidgetHeading title="Career Progress" /><div className="progress-head"><span>Progress toward {selectedJob?.title || 'your target role'}</span><strong>{Math.round(score)}%</strong></div><div className="progress-track"><i style={{ width: `${score}%` }} /></div><div className="milestones">{[{ label: 'Profile', done: true, icon: UserRound }, { label: 'Skills', done: skills.length > 0, icon: Settings2 }, { label: 'Jobs', done: recommendations.length > 0, icon: BriefcaseBusiness }, { label: 'Roadmap', done: Boolean(roadmap), icon: MapPinned }, { label: 'Goal', done: missing.length === 0 && Boolean(gap), icon: Target }].map(({ label, done, icon: Icon }, index) => <div className={`milestone ${done ? 'milestone-done' : ''}`} key={label}><span className="milestone-node"><Icon size={13} /></span><small>{label}</small>{index < 4 && <i className={`milestone-line ${done ? 'done-line' : ''}`} />}</div>)}</div></section>

            <section className="widget course-widget" id="recommended-courses"><WidgetHeading title="Recommended Courses" action="View All" onAction={() => jumpTo('#all-courses')} /><div className="course-list">{courses.slice(0, 3).map((course, index) => <a className="course-row" href={course.url} target="_blank" rel="noreferrer" key={course.course_id}><span className={`course-icon course-icon-${index}`}><BookOpen size={17} /></span><span className="course-copy"><strong>{course.course_name}</strong><small>{course.skill} · {course.platform}</small><span><i>{course.level}</i><Clock3 size={11} />{course.duration}</span></span><ChevronRight size={15} /></a>)}{!courses.length && <EmptyState text={gap ? 'No configured courses for the remaining skills.' : 'Run a skill-gap analysis to find courses.'} />}</div></section>

            <section className="widget roadmap-widget" id="career-roadmap"><WidgetHeading title="Your Learning Roadmap" action="View All" onAction={() => jumpTo('#full-roadmap')} /><div className="roadmap-compact">{roadmap?.steps?.slice(0, 6).map((step, index) => <div className="roadmap-step" key={step.skill}><span className={`roadmap-marker ${index === 0 ? 'roadmap-current' : ''}`}>{index === 0 ? <Check size={11} /> : null}</span><strong>Phase {step.order}</strong><span className="roadmap-topic">{step.skill}</span><small className={index === 0 ? 'status-current' : ''}>{index === 0 ? 'In Progress' : 'Not Started'}</small></div>)}{!roadmap?.steps?.length && <EmptyState text="Your roadmap appears after role analysis." />}</div></section>
          </section>

          <section className="workspace-tools" id="target-role"><section className="widget tool-widget"><WidgetHeading title="Target Role & Resume Analyzer" /><div className="tool-layout"><div className="role-control"><label htmlFor="target-job">Choose a role to compare against</label><select id="target-job" value={selected} onChange={(event) => { setSelected(event.target.value); setGap(null); setRoadmap(null); setCourses([]); }}><option value="">Select target job</option>{jobs.map((job) => <option key={job.job_id} value={job.job_id}>{job.title} · {job.company}</option>)}</select><button className="button-primary" onClick={() => loadDashboard(selected, skills)} disabled={!selected || loading === 'analysis'}>{loading === 'analysis' ? <LoaderCircle className="spin" size={16} /> : <Target size={16} />}Analyze role fit</button></div>
            <div className="resume-control" id="resume-analyzer"><div className="resume-icon"><FileText size={20} /></div><div><strong>Resume Analyzer</strong><p>Upload a PDF, DOCX, or TXT resume to add recognized skills to your profile.</p><label className="upload-button" htmlFor="resume-file">{loading === 'resume' ? <LoaderCircle className="spin" size={15} /> : <UploadCloud size={15} />}{loading === 'resume' ? 'Reading resume...' : 'Choose resume'}</label><input id="resume-file" type="file" accept=".pdf,.docx,.txt" onChange={uploadResume} /></div></div></div>
            {gap && <div className="analysis-result"><div><span className="result-label">Matched Skills</span><p>{matched.join(' · ') || 'No matches yet'}</p></div><div><span className="result-label">Missing Skills</span><p className="missing-copy">{missing.join(' · ') || 'No gaps for this role'}</p></div><strong>{score}% <small>match</small></strong></div>}
          </section>

          <section className="widget tools-skills" id="my-skills"><WidgetHeading title="Manage Your Skills" /><p className="tool-description">Select skills from the catalog, or add another skill to your working profile.</p><div className="catalog-skills">{catalog.map((skill) => <button className={skills.includes(skill) ? 'catalog-chip chip-selected' : 'catalog-chip'} key={skill} aria-pressed={skills.includes(skill)} onClick={() => toggleSkill(skill)}>{skill}</button>)}</div><form className="add-skill-form" onSubmit={addSkill}><input aria-label="Add another skill" placeholder="Add another skill" value={newSkill} onChange={(event) => setNewSkill(event.target.value)} /><button className="icon-control add-skill-button" aria-label="Add skill" type="submit"><Plus size={17} /></button></form><div className="selected-skill-list"><span className="result-label">Selected skills</span><div>{skills.map((skill) => <span className="selected-chip" key={skill}>{skill}<button aria-label={`Remove ${skill}`} onClick={() => toggleSkill(skill)}><X size={12} /></button></span>)}</div></div></section></section>

          <section className="widget full-list-widget" id="all-jobs"><WidgetHeading title="All Job Matches" /><div className="full-job-list">{filteredJobs.map((job, index) => <JobRow key={job.job_id} job={job} index={index} />)}</div></section>
          <section className="widget full-list-widget" id="full-roadmap"><WidgetHeading title={`Roadmap${selectedJob ? ` · ${selectedJob.title}` : ''}`} />{roadmap?.steps?.length ? <ol className="full-roadmap-list">{roadmap.steps.map((step, index) => <li key={step.skill}><span>{String(step.order).padStart(2, '0')}</span><div><strong>{step.skill}</strong><p>{step.focus}</p>{step.resource_url && <a href={step.resource_url} target="_blank" rel="noreferrer">{step.resource_title} <ArrowUpRight size={13} /></a>}</div><small>{index === 0 ? 'In Progress' : `~${step.duration_weeks} week`}</small></li>)}</ol> : <EmptyState text="Select a target role and analyze your skills to generate a roadmap." />}</section>
          <section className="widget full-list-widget" id="all-courses"><WidgetHeading title="Courses for Your Skill Gaps" /><div className="all-courses-list">{courses.map((course) => <a className="all-course-row" href={course.url} target="_blank" rel="noreferrer" key={course.course_id}><BookOpen size={17} /><span><strong>{course.course_name}</strong><small>{course.skill} · {course.platform} · {course.level} · {course.duration}</small></span><ArrowUpRight size={15} /></a>)}</div></section>
          <footer className="dashboard-footer"><span>Build Your Future with AI-Powered Career Guidance</span><span><button onClick={() => jumpTo('#dashboard')}>Learn</button><button onClick={() => jumpTo('#skill-gap')}>Improve</button><button onClick={() => jumpTo('#career-roadmap')}>Get Hired</button></span></footer>
        </main>
      </div>

      {profileOpen && <div className="modal-scrim" onMouseDown={(event) => { if (event.target === event.currentTarget) setProfileOpen(false); }}><form className="profile-modal" onSubmit={saveProfile}><button type="button" className="modal-close icon-control" aria-label="Close" onClick={() => setProfileOpen(false)}><X size={18} /></button><span className="modal-eyebrow">STUDENT PROFILE</span><h2>Edit Profile</h2><div className="profile-fields">{[['name', 'Name'], ['email', 'Email'], ['phone', 'Phone'], ['education', 'Education'], ['degree', 'Degree'], ['graduation_year', 'Graduation year'], ['experience', 'Experience'], ['location', 'Location'], ['preferred_job_role', 'Preferred job role'], ['preferred_location', 'Preferred location']].map(([key, label]) => <label key={key}>{label}<input type={key === 'graduation_year' ? 'number' : key === 'email' ? 'email' : 'text'} value={profile[key] || ''} onChange={(event) => setProfile((current) => ({ ...current, [key]: event.target.value }))} /></label>)}</div><div className="modal-actions"><button type="button" className="button-secondary" onClick={() => setProfileOpen(false)}>Cancel</button><button className="button-primary" type="submit" disabled={loading === 'profile'}>{loading === 'profile' ? 'Saving...' : 'Save Profile'}</button></div></form></div>}
      {authMode && <div className="modal-scrim" onMouseDown={(event) => { if (event.target === event.currentTarget) setAuthMode(''); }}><form className="profile-modal auth-modal" onSubmit={submitAuth}><button type="button" className="modal-close icon-control" aria-label="Close" onClick={() => setAuthMode('')}><X size={18} /></button><span className="modal-eyebrow">SKILLBRIDGE ACCOUNT</span><h2>{authMode === 'register' ? 'Create your account' : 'Welcome back'}</h2>{authMode === 'register' && <label>Name<input required minLength="2" value={authForm.name} onChange={(event) => setAuthForm((current) => ({ ...current, name: event.target.value }))} /></label>}<label>Email<input required type="email" value={authForm.email} onChange={(event) => setAuthForm((current) => ({ ...current, email: event.target.value }))} /></label><label>Password<input required minLength="8" type="password" value={authForm.password} onChange={(event) => setAuthForm((current) => ({ ...current, password: event.target.value }))} /></label><button className="button-primary" type="submit" disabled={loading === 'auth'}>{loading === 'auth' ? 'Please wait...' : authMode === 'register' ? 'Create account' : 'Sign in'}</button><button type="button" className="auth-switch" onClick={() => setAuthMode(authMode === 'register' ? 'login' : 'register')}>{authMode === 'register' ? 'Already registered? Sign in' : 'New here? Create an account'}</button></form></div>}
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color, foot, progress }) {
  return <article className={`stat-card stat-${color}`}><span className="stat-icon"><Icon size={19} /></span><div className="stat-copy"><span>{label}</span><strong>{value}</strong>{progress !== undefined ? <div className="stat-progress"><i style={{ width: `${progress}%` }} /></div> : <small>{foot}</small>}</div>{progress !== undefined && <small className="stat-foot">{foot}</small>}</article>;
}

function WidgetHeading({ title, action, onAction }) {
  return <div className="widget-heading"><h2>{title}</h2>{action && <button onClick={onAction}>{action}<ChevronRight size={13} /></button>}</div>;
}

function JobRow({ job, index }) {
  return <article className="job-row"><span className={`job-company-icon company-icon-${index % 4}`}><BriefcaseBusiness size={16} /></span><span className="job-row-copy"><strong>{job.title}</strong><small>{job.company}<i /><MapPin size={11} />{job.location}</small></span><span className="job-match">{Math.round(job.match_percentage)}% Match</span></article>;
}

function EmptyState({ text }) {
  return <div className="empty-state"><Activity size={17} /><span>{text}</span></div>;
}

createRoot(document.getElementById('root')).render(<App />);