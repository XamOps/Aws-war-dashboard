import React, { useState, useEffect, useCallback } from 'react';
import { Shield, DollarSign, BarChart2, HardDrive, LogOut, AlertTriangle, CheckCircle, Bell, User, ChevronsRight, Zap, Layers, Activity, RefreshCw, UserX, Lock, Key, ShieldOff, FileText, WifiOff, Archive, Database, Disc, GaugeCircle, GitBranch } from 'lucide-react';
import { Radar, Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, RadialLinearScale, PointElement, LineElement, Filler } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, RadialLinearScale, PointElement, LineElement, Filler);

// Animation styles to be injected
const animationStyles = `
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.finding-card {
  animation: fadeInUp 0.5s ease-out forwards;
  opacity: 0; /* Start as transparent, animation will make it visible */
}
/* Apply animation delay to each card */
.finding-card:nth-child(1) { animation-delay: 0.1s; }
.finding-card:nth-child(2) { animation-delay: 0.2s; }
.finding-card:nth-child(3) { animation-delay: 0.3s; }
.finding-card:nth-child(4) { animation-delay: 0.4s; }
.finding-card:nth-child(5) { animation-delay: 0.5s; }
.finding-card:nth-child(6) { animation-delay: 0.6s; }
`;


// --- Caching Configuration ---
const CACHE_KEY = 'awsWarDashboardData';
const CACHE_DURATION_MS = 60 * 60 * 1000; // 1 hour

// --- AWS Logo Component ---
const AwsLogo = (props) => (
  <svg
    {...props}
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 128 128"
    aria-label="AWS Logo"
  >
    <path
      fill="#FF9900"
      d="M59.34 94.25a7.35 7.35 0 0 1-5.73-2.58L20.15 47.38a7.35 7.35 0 0 1 11.47-9.25l32.53 40.2a1 1 0 0 0 1.52-.16l32.55-40.18a7.35 7.35 0 1 1 11.46 9.25L65.08 91.67a7.35 7.35 0 0 1-5.74 2.58z"
    />
    <path
      fill="#232F3E"
      d="M74.45 81.39a7.35 7.35 0 0 1-6-2.8L25.41 23.3A7.35 7.35 0 0 1 37 14.12l42.2 52.1a1 1 0 0 0 1.58-.1l42.2-52.1a7.35 7.35 0 1 1 11.6 9.18L80.45 78.59a7.35 7.35 0 0 1-6 2.8z"
    />
  </svg>
);


// --- Reusable UI Components ---
const Sidebar = ({ activeTab, setActiveTab, isOpen, setIsOpen }) => {
    const navItems = [
        { id: 'dashboard', icon: BarChart2, label: 'Dashboard' },
        { id: 'security', icon: Shield, label: 'Security' },
        { id: 'cost', icon: DollarSign, label: 'Cost Optimization' },
        { id: 'reliability', icon: HardDrive, label: 'Reliability' },
        { id: 'performance', icon: Zap, label: 'Performance' },
        { id: 'operations', icon: Layers, label: 'Operations' },
    ];
    return (
        <div className={`fixed top-0 left-0 h-full bg-gray-800 text-white flex flex-col transition-all duration-300 ${isOpen ? 'w-64' : 'w-20'}`}>
            <div className={`p-5 border-b border-gray-700 flex items-center space-x-3 ${!isOpen && 'justify-center'}`}>
                <AwsLogo className="w-10 h-10 flex-shrink-0"/>
                <h1 className={`text-2xl font-bold transition-opacity duration-200 whitespace-nowrap ${!isOpen && 'opacity-0'}`}>AWS WAR</h1>
            </div>
            <nav className="flex-grow mt-5 px-2">
                {navItems.map(item => (
                    <button 
                        key={item.id} 
                        onClick={() => setActiveTab(item.id)} 
                        className={`flex items-center w-full text-left p-3 text-sm font-medium rounded-md transition-colors duration-200 ${activeTab === item.id ? 'bg-gray-900 text-white' : 'text-gray-400 hover:bg-gray-700'} ${!isOpen && 'justify-center'}`}
                        title={isOpen ? "" : item.label}
                    >
                        <item.icon className="w-5 h-5 flex-shrink-0" />
                        <span className={`ml-3 transition-opacity duration-200 whitespace-nowrap ${!isOpen && 'opacity-0'}`}>{item.label}</span>
                    </button>
                ))}
            </nav>
            {/* Pinned bottom section */}
            <div className="border-t border-gray-700 p-2">
                 <button onClick={() => setIsOpen(!isOpen)} className={`flex items-center w-full p-3 text-sm font-medium rounded-md text-gray-400 hover:bg-gray-700 transition-colors duration-200 ${!isOpen && 'justify-center'}`}>
                    <ChevronsRight className={`w-5 h-5 transition-transform duration-300 ${isOpen && 'rotate-180'}`} />
                    <span className={`ml-3 transition-opacity duration-200 whitespace-nowrap ${!isOpen && 'opacity-0'}`}>Collapse</span>
                </button>
                 <button onClick={() => {}} className={`flex items-center w-full p-3 text-sm font-medium rounded-md text-gray-400 hover:bg-gray-700 transition-colors duration-200 ${!isOpen && 'justify-center'}`}>
                    <LogOut className="w-5 h-5 flex-shrink-0" />
                    <span className={`ml-3 transition-opacity duration-200 whitespace-nowrap ${!isOpen && 'opacity-0'}`}>Logout</span>
                </button>
            </div>
        </div>
    );
};

const Header = ({ title, onRefresh }) => ( 
    <div className="flex items-center justify-between h-16 bg-white border-b border-gray-200 px-8">
        <div>
            <h2 className="text-xl font-semibold text-gray-800">{title}</h2>
        </div>
        <div className="flex items-center space-x-6">
            <button onClick={onRefresh} className="flex items-center space-x-2 text-gray-500 hover:text-blue-600 transition-colors" title="Refresh Data">
                <RefreshCw className="w-5 h-5" />
                <span className="text-sm">Refresh</span>
            </button>
            <button className="relative text-gray-500 hover:text-gray-800">
                <Bell className="w-6 h-6" />
                <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
            <div className="flex items-center">
                <User className="w-8 h-8 rounded-full bg-gray-200 text-gray-600 p-1" />
                <div className="ml-3">
                    <p className="text-sm font-medium text-gray-800">Local User</p>
                    <p className="text-xs text-gray-500">Default Credentials</p>
                </div>
            </div>
        </div>
    </div>
);

const SummaryCard = ({ title, value, icon, color }) => { const Icon = icon; return ( <div className="bg-white p-6 rounded-lg shadow-md flex items-center transition-transform hover:scale-105"> <div className={`p-3 rounded-full bg-${color}-100 text-${color}-600 mr-4`}> <Icon className="w-6 h-6" /> </div> <div> <p className="text-sm text-gray-500">{title}</p> <p className="text-2xl font-bold text-gray-800">{value}</p> </div> </div> ); };

const FindingTable = ({ icon, title, columns, data, renderRow }) => {
    const Icon = icon;
    return (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden transition-all hover:shadow-xl finding-card">
            <div className="p-6 border-b border-gray-200">
                <div className="flex items-center">
                    {Icon && <Icon className="w-6 h-6 text-gray-500 mr-3" />}
                    <h3 className="text-xl font-bold text-gray-800">{title}</h3>
                </div>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left text-gray-600">
                    <thead className="text-xs text-gray-700 uppercase bg-gray-100 border-b border-gray-200">
                        <tr>
                            {columns.map(col => (
                                <th key={col} scope="col" className="px-6 py-4 font-bold">
                                    {col}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {data && data.length > 0 ? (
                            data.map((item, index) => renderRow(item, index))
                        ) : (
                            <tr>
                                <td colSpan={columns.length} className="px-6 py-10 text-center">
                                    <div className="flex flex-col items-center justify-center text-green-600">
                                        <CheckCircle className="w-12 h-12 mb-2" />
                                        <span className="font-semibold text-lg">All Clear!</span>
                                        <p className="text-sm text-gray-500">No issues found for this check.</p>
                                    </div>
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

const FullPageLoader = () => { 
    const [loadingText, setLoadingText] = useState('Connecting to AWS Account...'); 
    useEffect(() => { 
        const texts = [ "Scanning IAM for MFA Gaps...", "Analyzing S3 Bucket Policies...", "Checking Security Group Rules...", "Auditing for EBS Backup Policies...", "Verifying RDS Instance Configurations...", "Compiling Findings Report..." ]; 
        let index = 0; 
        const intervalId = setInterval(() => { 
            index = (index + 1) % texts.length; 
            setLoadingText(texts[index]); 
        }, 2000); 
        return () => clearInterval(intervalId); 
    }, []); 

    return ( 
        <div className="flex flex-col items-center justify-center h-full pt-20"> 
            <div className="relative"> 
                <Shield className="w-24 h-24 text-blue-500" /> 
                <div className="absolute inset-0 rounded-full border-4 border-blue-500 animate-ping"></div> 
            </div> 
            <h2 className="mt-8 text-xl font-semibold text-gray-600">Scanning Your Account</h2> 
            <p className="mt-2 text-gray-500 transition-all duration-300">{loadingText}</p> 
        </div> 
    ); 
};

const ApiHealthCard = ({ metadata }) => {
    if (!metadata) return null;
    const isHealthy = metadata.status === 'Healthy';
    const color = isHealthy ? 'green' : 'red';
    return (
        <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4 text-gray-700 flex items-center">
                <Activity className="w-5 h-5 mr-2" /> Scan & API Health
            </h3>
            <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                    <span className="text-gray-500">Scan Status:</span>
                    <span className={`font-medium text-${color}-600`}>{metadata.status}</span>
                </div>
                <div className="flex justify-between">
                    <span className="text-gray-500">Scan Duration:</span>
                    <span className="font-medium">{metadata.last_scan_duration_sec}s</span>
                </div>
                <div className="flex justify-between">
                    <span className="text-gray-500">Throttled API Calls:</span>
                    <span className={`font-bold ${metadata.throttled_requests > 0 ? 'text-red-500' : 'text-green-600'}`}>{metadata.throttled_requests}</span>
                </div>
            </div>
            <div className={`mt-4 p-2 text-xs text-center rounded-md bg-${color}-50 text-${color}-700`}>
                {isHealthy ? "All API requests were successful." : "Some API requests were throttled. Data may be incomplete."}
            </div>
        </div>
    )
}

// --- CHART COMPONENTS ---
const PillarRatingChart = ({ data }) => {
    const calculateScore = (findings) => Math.max(1, 5 - Math.floor(findings / 5));
    const getFindingCount = (pillarData) => pillarData ? Object.values(pillarData).flat().length : 0;
    const scores = { 
        Security: calculateScore(getFindingCount(data.security)), 
        Cost: calculateScore(getFindingCount(data.cost_optimization)), 
        Reliability: calculateScore(getFindingCount(data.reliability)), 
        Performance: calculateScore(getFindingCount(data.performance_efficiency)), 
        Operations: calculateScore(getFindingCount(data.operational_excellence)), 
    };
    const chartData = { 
        labels: Object.keys(scores), 
        datasets: [{ 
            label: 'Pillar Score (out of 5)', 
            data: Object.values(scores), 
            backgroundColor: 'rgba(59, 130, 246, 0.2)', 
            borderColor: 'rgba(59, 130, 246, 1)', 
            borderWidth: 2, 
            pointBackgroundColor: 'rgba(59, 130, 246, 1)', 
        }], 
    };
    const options = { 
        maintainAspectRatio: false, 
        scales: { 
            r: { 
                angleLines: { color: 'rgba(0, 0, 0, 0.1)' }, 
                grid: { color: 'rgba(0, 0, 0, 0.1)' }, 
                pointLabels: { font: { size: 12, weight: 'bold' } }, 
                ticks: { backdropColor: 'transparent', stepSize: 1, max: 5, min: 0 }, 
            } 
        }, 
        plugins: { 
            legend: { display: false } 
        }, 
    };
    return (
        <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4 text-gray-700">Well-Architected Pillar Ratings</h3>
            <div style={{ position: 'relative', height: '300px' }}>
                <Radar data={chartData} options={options} />
            </div>
        </div>
    );
};
const SecurityDoughnutChart = ({ data }) => {
    const findings = {
        'Users without MFA': data?.users_without_mfa?.length || 0,
        'Public S3 Buckets': data?.public_s3_buckets?.length || 0,
        'Aged IAM Keys': data?.aged_iam_keys?.length || 0,
        'Open Security Groups': data?.unrestricted_security_groups?.length || 0,
    };
    const chartData = {
        labels: Object.keys(findings),
        datasets: [{
            data: Object.values(findings),
            backgroundColor: ['#EF4444', '#F87171', '#FCA5A5', '#FECACA'],
            borderColor: '#FFFFFF',
            borderWidth: 2,
        }],
    };
    const options = { maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } };
    return (
        <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4 text-gray-700">Security Findings Breakdown</h3>
            <div style={{ position: 'relative', height: '300px' }}>
                <Doughnut data={chartData} options={options} />
            </div>
        </div>
    );
};

// --- DETAILED PAGE COMPONENTS ---

const DashboardPage = ({ data }) => {
    const getFindingCount = (pillarData) => pillarData ? Object.values(pillarData).flat().length : 0;
    return (
        <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                <SummaryCard title="Security Findings" value={getFindingCount(data.security)} icon={AlertTriangle} color="red" />
                <SummaryCard title="Cost Opportunities" value={getFindingCount(data.cost_optimization)} icon={DollarSign} color="yellow" />
                <SummaryCard title="Reliability Risks" value={getFindingCount(data.reliability)} icon={HardDrive} color="orange" />
                <SummaryCard title="Performance Gaps" value={getFindingCount(data.performance_efficiency)} icon={Zap} color="blue" />
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <PillarRatingChart data={data} />
                <SecurityDoughnutChart data={data.security} />
                <ApiHealthCard metadata={data.scan_metadata} />
            </div>
        </div>
    );
};

const SecurityPage = ({ data }) => (
    <div className="space-y-8">
        <FindingTable 
            icon={UserX}
            title="Users without MFA" 
            columns={['Username']} 
            data={data?.users_without_mfa || []} 
            renderRow={(item, index) => (
                <tr key={item} className={`border-b transition-colors duration-200 ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'} hover:bg-red-100`}>
                    <td className="px-6 py-4 font-medium text-gray-900">{item}</td>
                </tr>
            )}
        />
        <FindingTable 
            icon={Lock}
            title="Public S3 Buckets" 
            columns={['Bucket Name', 'Reason']} 
            data={data?.public_s3_buckets || []} 
            renderRow={(item, index) => (
                <tr key={item.Bucket} className={`border-b transition-colors duration-200 ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'} hover:bg-red-100`}>
                    <td className="px-6 py-4 font-mono text-gray-800">{item.Bucket}</td>
                    <td className="px-6 py-4"><span className="px-2 py-1 text-xs font-semibold text-yellow-800 bg-yellow-100 rounded-full">{item.Reason}</span></td>
                </tr>
            )} 
        />
        <FindingTable 
            icon={Key}
            title="Aged IAM Access Keys (> 90 days)" 
            columns={['Username', 'Access Key ID']} 
            data={data?.aged_iam_keys || []} 
            renderRow={(item, index) => (
                <tr key={item.AccessKeyId} className={`border-b transition-colors duration-200 ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'} hover:bg-red-100`}>
                    <td className="px-6 py-4 text-gray-900">{item.UserName}</td>
                    <td className="px-6 py-4 font-mono">{item.AccessKeyId}</td>
                </tr>
            )} 
        />
        <FindingTable 
            icon={ShieldOff}
            title="Unrestricted Security Groups (0.0.0.0/0)" 
            columns={['Group Name', 'Group ID', 'Port']} 
            data={data?.unrestricted_security_groups || []} 
            renderRow={(item, index) => (
                <tr key={item.GroupId+item.PortRange} className={`border-b transition-colors duration-200 ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'} hover:bg-red-100`}>
                    <td className="px-6 py-4">{item.GroupName}</td>
                    <td className="px-6 py-4 font-mono">{item.GroupId}</td>
                    <td className="px-6 py-4"><span className="px-2 py-1 font-mono text-xs font-semibold text-purple-800 bg-purple-100 rounded-full">{String(item.PortRange)}</span></td>
                </tr>
            )}
        />
        <FindingTable 
            icon={WifiOff}
            title="VPCs without Flow Logs" 
            columns={['VPC ID']} 
            data={data?.vpcs_without_flow_logs || []} 
            renderRow={(item, index) => (
                <tr key={item} className={`border-b transition-colors duration-200 ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'} hover:bg-red-100`}>
                    <td className="px-6 py-4 font-mono">{item}</td>
                </tr>
            )} 
        />
        <FindingTable 
            icon={FileText}
            title="CloudTrail Status" 
            columns={['Trail Name', 'Status']} 
            data={data?.cloudtrail_status?.filter(t => !t.IsLogging) || []} 
            renderRow={(item, index) => (
                <tr key={item.Name} className={`border-b transition-colors duration-200 ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'} hover:bg-red-100`}>
                    <td className="px-6 py-4">{item.Name}</td>
                    <td className="px-6 py-4"><span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"><AlertTriangle className="w-3 h-3 mr-1.5" />Not Logging</span></td>
                </tr>
            )} 
        />
    </div>
);

const ComputeOptimizerCard = ({ data }) => (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden finding-card">
        <div className="p-6">
            <div className="flex items-center">
                <DollarSign className="w-6 h-6 text-gray-500 mr-3" />
                <h3 className="text-xl font-bold text-gray-800">Compute Optimizer Status</h3>
            </div>
            <div className="mt-4">
                {data?.error ? (
                    <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                        <div className="flex">
                            <div className="flex-shrink-0">
                                <AlertTriangle className="h-5 w-5 text-yellow-400" aria-hidden="true" />
                            </div>
                            <div className="ml-3">
                                <p className="text-sm text-yellow-700">
                                    Not Enabled. {' '}
                                    <span className="font-medium text-yellow-800">You must opt-in to get cost-saving recommendations for EC2.</span>
                                </p>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="bg-green-50 border-l-4 border-green-400 p-4">
                        <div className="flex">
                            <div className="flex-shrink-0">
                                <CheckCircle className="h-5 w-5 text-green-400" aria-hidden="true" />
                            </div>
                            <div className="ml-3">
                                <p className="text-sm text-green-700">
                                    Enabled. {' '}
                                    <span className="font-medium text-green-800">Check the Compute Optimizer console for recommendations.</span>
                                </p>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    </div>
);

const CostPage = ({ data }) => (
    <div className="space-y-8">
        <FindingTable 
            icon={Archive}
            title="S3 Buckets without Lifecycle Policies" 
            columns={['Bucket Name']} 
            data={data?.s3_buckets_without_lifecycle || []} 
            renderRow={(item, index) => (
                <tr key={item} className={`border-b transition-colors duration-200 ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'} hover:bg-yellow-100`}>
                    <td className="px-6 py-4 font-mono">{item}</td>
                </tr>
            )}
        />
        <ComputeOptimizerCard data={data?.compute_optimizer_status} />
    </div>
);

const ReliabilityPage = ({ data }) => (
    <div className="space-y-8">
        <FindingTable 
            icon={Database}
            title="RDS Instances not Multi-AZ" 
            columns={['DB Identifier', 'Engine', 'Multi-AZ Status']}
            data={data?.rds_multi_az_status?.filter(db => !db.IsMultiAZ) || []} 
            renderRow={(item, index) => (
                <tr key={item.DBInstanceIdentifier} className={`border-b transition-colors duration-200 ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'} hover:bg-orange-100`}>
                    <td className="px-6 py-4 font-medium">{item.DBInstanceIdentifier}</td>
                    <td className="px-6 py-4">{item.Engine}</td>
                    <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            <AlertTriangle className="w-3 h-3 mr-1.5" />
                            Disabled
                        </span>
                    </td>
                </tr>
            )}
        />
        <FindingTable 
            icon={Disc}
            title="EBS Volumes without Recent Backups" 
            columns={['Volume ID', 'Size (GiB)', 'Backup Status']}
            data={data?.ebs_volumes_without_backup || []} 
            renderRow={(item, index) => (
                <tr key={item.VolumeId} className={`border-b transition-colors duration-200 ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'} hover:bg-orange-100`}>
                    <td className="px-6 py-4 font-mono">{item.VolumeId}</td>
                    <td className="px-6 py-4">{item.SizeGiB}</td>
                    <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                             <AlertTriangle className="w-3 h-3 mr-1.5" />
                            Not Found
                        </span>
                    </td>
                </tr>
            )}
        />
    </div>
);

const PerformancePage = ({ data }) => (
    <div className="space-y-8">
        <FindingTable 
            icon={GaugeCircle}
            title="EC2 Instances without Detailed Monitoring" 
            columns={['Instance Name', 'Instance ID', 'Monitoring Level']}
            data={data?.ec2_without_detailed_monitoring || []} 
            renderRow={(item, index) => (
                <tr key={item.InstanceId} className={`border-b transition-colors duration-200 ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'} hover:bg-blue-100`}>
                    <td className="px-6 py-4">{item.Name}</td>
                    <td className="px-6 py-4 font-mono">{item.InstanceId}</td>
                    <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            <AlertTriangle className="w-3 h-3 mr-1.5" />
                            Basic
                        </span>
                    </td>
                </tr>
            )} 
        />
    </div>
);

const OperationsPage = ({ data }) => (
    <div className="space-y-8">
        <FindingTable 
            icon={GitBranch}
            title="CloudFormation Stacks with Drift" 
            columns={['Stack Name', 'Drift Status']} 
            data={data?.cloudformation_drift_status || []} 
            renderRow={(item, index) => (
                <tr key={item.StackName} className={`border-b transition-colors duration-200 ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'} hover:bg-indigo-100`}>
                    <td className="px-6 py-4">{item.StackName}</td>
                    <td className="px-6 py-4"><span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">{item.DriftStatus}</span></td>
                </tr>
            )} 
        />
    </div>
);


// --- MAIN APP COMPONENT ---
const App = () => {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isSidebarOpen, setSidebarOpen] = useState(true);

    const fetchData = useCallback(async (forceRefresh = false) => {
        setLoading(true);
        setError(null);

        if (!forceRefresh) {
            try {
                const cachedData = localStorage.getItem(CACHE_KEY);
                if (cachedData) {
                    const { timestamp, data: parsedData } = JSON.parse(cachedData);
                    if (Date.now() - timestamp < CACHE_DURATION_MS) {
                        console.log("Loading data from fresh cache.");
                        setData(parsedData);
                        setLoading(false);
                        return; // Exit if fresh cache is available
                    }
                    console.log("Stale cache found, will use it and refetch in background.");
                    setData(parsedData); // Show stale data immediately
                }
            } catch (e) {
                console.error("Failed to read from cache", e);
            }
        }
        
        try {
            const response = await fetch('http://127.0.0.1:5001/api/scan/all');
            if (!response.ok) throw new Error(`API request failed with status ${response.status}`);
            const result = await response.json();
            
            // Set data and update cache
            setData(result);
            localStorage.setItem(CACHE_KEY, JSON.stringify({
                timestamp: Date.now(),
                data: result,
            }));

        } catch (err) {
            console.error('Error fetching data:', err);
            setError('Failed to load data from API. Please ensure the backend server is running and reachable.');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);
    
    const handleRefresh = () => {
        console.log("Forcing data refresh...");
        localStorage.removeItem(CACHE_KEY);
        setData(null); // Clear existing data to show loader
        fetchData(true);
    };

    const pageTitles = {
        dashboard: 'Dashboard',
        security: 'Security Pillar Details',
        cost: 'Cost Optimization Details',
        reliability: 'Reliability Pillar Details',
        performance: 'Performance Efficiency Details',
        operations: 'Operational Excellence Details',
    };

    const renderContent = () => {
        if (loading && !data) return <FullPageLoader />; // Only show full loader if no data (even stale) is available
        if (error && !data) return ( <div className="p-8 text-center"><div className="max-w-md mx-auto bg-red-50 p-6 rounded-lg border border-red-200"><AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" /><h3 className="font-bold text-lg text-red-700 mb-2">Data Loading Error</h3><p className="text-red-600 mb-4">{error}</p><button onClick={handleRefresh} className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors">Retry</button></div></div> );
        if (!data) return <div className="p-8 text-center text-gray-500">No data available to display.</div>;

        switch (activeTab) {
            case 'dashboard': return <DashboardPage data={data} />;
            case 'security': return <SecurityPage data={data.security} />;
            case 'cost': return <CostPage data={data.cost_optimization} />;
            case 'reliability': return <ReliabilityPage data={data.reliability} />;
            case 'performance': return <PerformancePage data={data.performance_efficiency} />;
            case 'operations': return <OperationsPage data={data.operational_excellence} />;
            default: return <DashboardPage data={data} />;
        }
    };

    return (
        <div className="bg-gray-100 min-h-screen">
            <style>{animationStyles}</style>
            <Sidebar 
                activeTab={activeTab} 
                setActiveTab={setActiveTab}
                isOpen={isSidebarOpen}
                setIsOpen={setSidebarOpen} 
            />
            <div className={`transition-all duration-300 ${isSidebarOpen ? 'ml-64' : 'ml-20'}`}>
                <Header title={pageTitles[activeTab]} onRefresh={handleRefresh} />
                <main className="p-8">
                    {renderContent()}
                </main>
            </div>
        </div>
    );
};

export default App;
