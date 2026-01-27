import React, { useState } from 'react';

const SangoTextSimDemo = () => {
  const [view, setView] = useState('map');
  const [selectedCity, setSelectedCity] = useState(null);
  const [showDuel, setShowDuel] = useState(false);
  const [duelHP, setDuelHP] = useState({ player: 100, enemy: 100 });
  const [duelLog, setDuelLog] = useState([]);

  const cities = {
    chengdu: { name: '成都 Chengdu', faction: 'shu', gold: 12400, food: 89000, troops: 35000, defense: 340, x: 25, y: 70 },
    hanzhong: { name: '漢中 Hanzhong', faction: 'cao', gold: 8200, food: 45000, troops: 28000, defense: 280, x: 35, y: 45 },
    luoyang: { name: '洛陽 Luoyang', faction: 'cao', gold: 28000, food: 120000, troops: 65000, defense: 450, x: 50, y: 35 },
    jianye: { name: '建業 Jianye', faction: 'wu', gold: 22000, food: 95000, troops: 48000, defense: 380, x: 75, y: 55 },
    xiangyang: { name: '襄陽 Xiangyang', faction: 'cao', gold: 15000, food: 68000, troops: 42000, defense: 320, x: 55, y: 50 },
  };

  const factionColors = {
    shu: 'text-green-400',
    cao: 'text-blue-400',
    wu: 'text-red-400',
  };

  const officers = [
    { name: '關羽', nameEn: 'Guan Yu', war: 97, int: 78, pol: 62, cha: 93, traits: ['Brave', 'Proud'], ability: 'Green Dragon Slash' },
    { name: '張飛', nameEn: 'Zhang Fei', war: 98, int: 42, pol: 38, cha: 56, traits: ['Fierce', 'Impulsive'], ability: 'Thunderous Roar' },
    { name: '趙雲', nameEn: 'Zhao Yun', war: 96, int: 74, pol: 65, cha: 82, traits: ['Loyal', 'Brave'], ability: 'Lone Rider' },
    { name: '諸葛亮', nameEn: 'Zhuge Liang', war: 55, int: 100, pol: 95, cha: 92, traits: ['Strategist', 'Cautious'], ability: 'Empty Fort Strategy' },
  ];

  const handleDuelAction = (action) => {
    const playerRoll = Math.random() * 100;
    const enemyRoll = Math.random() * 100;
    let playerDmg = 0;
    let enemyDmg = 0;
    let log = '';

    if (action === 'attack') {
      playerDmg = playerRoll > 40 ? Math.floor(15 + Math.random() * 10) : 0;
      enemyDmg = enemyRoll > 50 ? Math.floor(10 + Math.random() * 8) : 0;
      log = playerDmg > 0 
        ? `⚔️ Zhao Yun strikes! ${playerDmg} damage!`
        : `💨 Xiahou Dun parries your attack!`;
    } else if (action === 'defend') {
      enemyDmg = Math.floor((10 + Math.random() * 8) * 0.5);
      log = `🛡️ You brace for impact. Reduced damage: ${enemyDmg}`;
    } else if (action === 'special') {
      if (Math.random() > 0.4) {
        playerDmg = Math.floor(25 + Math.random() * 15);
        log = `🐉 DRAGON PIERCES THE CLOUDS! ${playerDmg} massive damage!`;
      } else {
        log = `💨 Your special attack misses! You're left vulnerable!`;
        enemyDmg = Math.floor(15 + Math.random() * 10);
      }
    }

    const newPlayerHP = Math.max(0, duelHP.player - enemyDmg);
    const newEnemyHP = Math.max(0, duelHP.enemy - playerDmg);

    setDuelHP({ player: newPlayerHP, enemy: newEnemyHP });
    setDuelLog(prev => [...prev.slice(-4), log, enemyDmg > 0 ? `⚔️ Xiahou Dun counters for ${enemyDmg}!` : ''].filter(Boolean));
  };

  const renderMap = () => (
    <div className="font-mono text-xs leading-tight">
      <div className="text-yellow-400 text-center mb-2 text-sm">═══════════ CHINA - Spring 194 AD ═══════════</div>
      <pre className="text-gray-300 whitespace-pre">
{`
                              ╔═══════╗
                              ║ 幽 州 ║ 
                              ╚═══╦═══╝
                                  ║
           ╔═══════╗          ╔═══╩═══╗          ╔═══════╗
           ║ 并 州 ║──────────║ 冀 州 ║──────────║ 青 州 ║
           ╚═══╦═══╝          ╚═══╦═══╝          ╚═══════╝
               ║                  ║
           ╔═══╩═══╗          ╔═══╩═══╗          ╔═══════╗
           ║ 雍 州 ║──────────║`}<span className="text-blue-400"> 洛 陽 </span>{`║──────────║ 徐 州 ║
           ╚═══╦═══╝          ╚═══╦═══╝          ╚═══════╝
               ║                  ║
           ╔═══╩═══╗          ╔═══╩═══╗          ╔═══════╗
           ║`}<span className="text-blue-400"> 漢 中 </span>{`║──────────║`}<span className="text-blue-400"> 襄 陽 </span>{`║──────────║`}<span className="text-red-400"> 建 業 </span>{`║
           ╚═══╦═══╝          ╚═══════╝          ╚═══════╝
               ║                  
           ╔═══╩═══╗          ╔═══════╗          ╔═══════╗
           ║`}<span className="text-green-400"> 成 都 </span>{`║──────────║ 荊 南 ║──────────║ 交 州 ║
           ╚═══════╝          ╚═══════╝          ╚═══════╝
`}
      </pre>
      <div className="flex justify-center gap-4 mt-2 text-xs">
        <span className="text-green-400">■ 蜀 Shu (You)</span>
        <span className="text-blue-400">■ 魏 Wei (Cao)</span>
        <span className="text-red-400">■ 吳 Wu (Sun)</span>
        <span className="text-gray-400">■ Neutral</span>
      </div>
    </div>
  );

  const renderCityDetail = () => (
    <div className="font-mono text-xs">
      <div className="border border-yellow-600 rounded p-3 bg-gray-900">
        <div className="text-yellow-400 text-center text-sm mb-2">📍 CHENGDU (成都) - Your Capital</div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-gray-400 mb-1">RESOURCES</div>
            <div className="text-yellow-300">💰 Gold: 12,400</div>
            <div className="text-green-300">🍚 Food: 89,000</div>
            <div className="text-red-300">⚔️ Troops: 35,000</div>
            <div className="text-blue-300">🏰 Defense: 340</div>
          </div>
          <div>
            <div className="text-gray-400 mb-1">DEVELOPMENT</div>
            <div className="flex items-center gap-1">
              <span className="w-16">🌾 Farm:</span>
              <div className="bg-gray-700 h-2 w-24 rounded">
                <div className="bg-green-500 h-2 rounded" style={{width: '82%'}}></div>
              </div>
              <span className="text-green-400">82</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-16">💹 Trade:</span>
              <div className="bg-gray-700 h-2 w-24 rounded">
                <div className="bg-yellow-500 h-2 rounded" style={{width: '64%'}}></div>
              </div>
              <span className="text-yellow-400">64</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-16">📚 Tech:</span>
              <div className="bg-gray-700 h-2 w-24 rounded">
                <div className="bg-blue-500 h-2 rounded" style={{width: '54%'}}></div>
              </div>
              <span className="text-blue-400">54</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-16">🏰 Walls:</span>
              <div className="bg-gray-700 h-2 w-24 rounded">
                <div className="bg-gray-400 h-2 rounded" style={{width: '78%'}}></div>
              </div>
              <span className="text-gray-300">78</span>
            </div>
          </div>
        </div>
        <div className="mt-3 border-t border-gray-700 pt-2">
          <div className="text-gray-400 mb-1">STATIONED OFFICERS</div>
          <div className="grid grid-cols-2 gap-1 text-xs">
            {officers.map((o, i) => (
              <div key={i} className="flex items-center gap-2 bg-gray-800 p-1 rounded">
                <span className="text-yellow-400">{o.name}</span>
                <span className="text-gray-500">WAR:{o.war}</span>
                <span className="text-green-600">[{o.traits[0]}]</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderOfficer = () => (
    <div className="font-mono text-xs">
      <div className="border border-green-600 rounded p-3 bg-gray-900">
        <div className="flex gap-4">
          <div className="border border-gray-600 p-2 text-center bg-gray-800">
            <pre className="text-green-400 text-xs leading-none">
{`  ╭───╮
  │ 雲 │
  │ ─── │
  │ ╱│╲ │
  ╰─┴─╯`}
            </pre>
            <div className="text-yellow-400 mt-1">趙雲</div>
            <div className="text-gray-400">Zhao Yun</div>
          </div>
          <div className="flex-1">
            <div className="text-green-400 text-sm mb-2">⚔️ "God of War"</div>
            <div className="text-gray-400 italic text-xs mb-2">"I am the one who charges through ten thousand!"</div>
            <div className="grid grid-cols-2 gap-x-4 gap-y-1">
              <div className="flex items-center">
                <span className="w-12">⚔️ WAR:</span>
                <div className="bg-gray-700 h-1.5 w-16 rounded mr-1">
                  <div className="bg-red-500 h-1.5 rounded" style={{width: '96%'}}></div>
                </div>
                <span className="text-red-400">96</span>
              </div>
              <div className="flex items-center">
                <span className="w-12">📚 INT:</span>
                <div className="bg-gray-700 h-1.5 w-16 rounded mr-1">
                  <div className="bg-blue-500 h-1.5 rounded" style={{width: '74%'}}></div>
                </div>
                <span className="text-blue-400">74</span>
              </div>
              <div className="flex items-center">
                <span className="w-12">🏛️ POL:</span>
                <div className="bg-gray-700 h-1.5 w-16 rounded mr-1">
                  <div className="bg-yellow-500 h-1.5 rounded" style={{width: '65%'}}></div>
                </div>
                <span className="text-yellow-400">65</span>
              </div>
              <div className="flex items-center">
                <span className="w-12">👑 CHA:</span>
                <div className="bg-gray-700 h-1.5 w-16 rounded mr-1">
                  <div className="bg-purple-500 h-1.5 rounded" style={{width: '82%'}}></div>
                </div>
                <span className="text-purple-400">82</span>
              </div>
            </div>
            <div className="mt-2 flex gap-2">
              <span className="bg-red-900 text-red-300 px-2 py-0.5 rounded text-xs">勇猛 Brave</span>
              <span className="bg-blue-900 text-blue-300 px-2 py-0.5 rounded text-xs">忠義 Loyal</span>
            </div>
          </div>
        </div>
        <div className="mt-3 border-t border-gray-700 pt-2">
          <div className="text-yellow-400 mb-1">⚡ SPECIAL ABILITY: Lone Rider</div>
          <div className="text-gray-400 text-xs">Can break through enemy encirclement. +20% retreat success.</div>
        </div>
        <div className="mt-2 border-t border-gray-700 pt-2">
          <div className="text-gray-400 mb-1">RELATIONSHIPS</div>
          <div className="grid grid-cols-2 gap-1">
            <div className="flex items-center gap-1"><span>👑 劉備</span><span className="text-red-400">❤️❤️❤️❤️❤️</span></div>
            <div className="flex items-center gap-1"><span>⚔️ 關羽</span><span className="text-red-400">❤️❤️❤️❤️</span></div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderDuel = () => (
    <div className="font-mono text-xs">
      <div className="border border-red-600 rounded p-3 bg-gray-900">
        <div className="text-red-400 text-center text-sm mb-3">⚔️ DUEL: ZHAO YUN vs XIAHOU DUN ⚔️</div>
        
        <div className="flex justify-between mb-4">
          <div className="text-center">
            <div className="text-green-400">趙雲 Zhao Yun</div>
            <div className="text-xs text-gray-400">WAR: 96</div>
            <div className="bg-gray-700 h-3 w-32 rounded mt-1">
              <div 
                className="bg-green-500 h-3 rounded transition-all duration-300" 
                style={{width: `${duelHP.player}%`}}
              ></div>
            </div>
            <div className="text-green-400">{duelHP.player} HP</div>
          </div>
          <div className="text-yellow-400 text-2xl self-center">VS</div>
          <div className="text-center">
            <div className="text-blue-400">夏侯惇 Xiahou Dun</div>
            <div className="text-xs text-gray-400">WAR: 83</div>
            <div className="bg-gray-700 h-3 w-32 rounded mt-1">
              <div 
                className="bg-red-500 h-3 rounded transition-all duration-300" 
                style={{width: `${duelHP.enemy}%`}}
              ></div>
            </div>
            <div className="text-red-400">{duelHP.enemy} HP</div>
          </div>
        </div>

        <div className="bg-gray-800 p-2 rounded mb-3 h-20 overflow-y-auto">
          {duelLog.length === 0 ? (
            <div className="text-gray-500 text-center">The two generals face each other...</div>
          ) : (
            duelLog.map((log, i) => (
              <div key={i} className="text-gray-300">{log}</div>
            ))
          )}
        </div>

        {duelHP.player > 0 && duelHP.enemy > 0 ? (
          <div className="grid grid-cols-3 gap-2">
            <button 
              onClick={() => handleDuelAction('attack')}
              className="bg-red-800 hover:bg-red-700 text-white py-2 rounded transition"
            >
              ⚔️ Attack
            </button>
            <button 
              onClick={() => handleDuelAction('defend')}
              className="bg-blue-800 hover:bg-blue-700 text-white py-2 rounded transition"
            >
              🛡️ Defend
            </button>
            <button 
              onClick={() => handleDuelAction('special')}
              className="bg-yellow-800 hover:bg-yellow-700 text-white py-2 rounded transition"
            >
              🐉 Special
            </button>
          </div>
        ) : (
          <div className="text-center py-2">
            <div className={duelHP.player > 0 ? "text-green-400 text-lg" : "text-red-400 text-lg"}>
              {duelHP.player > 0 ? "🏆 VICTORY!" : "💀 DEFEAT!"}
            </div>
            <button 
              onClick={() => {
                setDuelHP({ player: 100, enemy: 100 });
                setDuelLog([]);
              }}
              className="mt-2 bg-gray-700 hover:bg-gray-600 text-white px-4 py-1 rounded"
            >
              Fight Again
            </button>
          </div>
        )}
      </div>
    </div>
  );

  const renderBattle = () => (
    <div className="font-mono text-xs">
      <div className="border border-orange-600 rounded p-3 bg-gray-900">
        <div className="text-orange-400 text-center text-sm mb-2">⚔️ BATTLE FOR HANZHONG - Turn 4 ⚔️</div>
        <pre className="text-gray-300 whitespace-pre text-center">
{`
                    ╔════════════════╗
                    ║  HANZHONG CITY ║
                    ║  🏰 DEF: 280   ║
                    ╚════════════════╝
                           │
      ════════════════════╪════════════════════ 〰️ River
           ╱               │               ╲
     [Mountain]       [Plains]        [Forest]
          │               │               │
     ┌────────┐      ┌────────┐      ┌────────┐
     │`}<span className="text-blue-400">夏侯淵</span>{`  │  ←→  │ `}<span className="text-orange-400">CLASH!</span>{` │  ←→  │`}<span className="text-green-400">黃 忠</span>{`  │
     │⚔️ 8,000│      │        │      │⚔️ 6,000│
     └────────┘      └────────┘      └────────┘
          │               ↑               │
          │          [Siege]              │
     ┌────────┐      ┌────────┐      ┌────────┐
     │`}<span className="text-blue-400">張 郃</span>{`  │      │`}<span className="text-green-400">劉 備</span>{`  │      │`}<span className="text-green-400">趙 雲</span>{`  │
     │⚔️12,000│      │⚔️15,000│      │⚔️10,000│
     └────────┘      └────────┘      └────────┘
`}
        </pre>
        <div className="flex justify-between text-xs mt-2 px-4">
          <span className="text-green-400">YOUR ARMY: 31,000</span>
          <span className="text-gray-400">SUPPLIES: 45 days</span>
          <span className="text-blue-400">ENEMY: 20,000</span>
        </div>
        <div className="mt-3 border-t border-gray-700 pt-2">
          <div className="text-yellow-400 mb-1">📜 Situation Report:</div>
          <div className="text-gray-400 italic">
            "My lord, Huang Zhong engages the enemy on the eastern forest. 
            Shall we support him or continue the siege?"
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2 mt-2">
          <button className="bg-red-800 hover:bg-red-700 text-white py-1 rounded text-xs">
            ⚔️ All-Out Attack
          </button>
          <button className="bg-blue-800 hover:bg-blue-700 text-white py-1 rounded text-xs">
            🏰 Continue Siege
          </button>
          <button className="bg-yellow-800 hover:bg-yellow-700 text-white py-1 rounded text-xs">
            🔥 Fire Attack
          </button>
          <button className="bg-green-800 hover:bg-green-700 text-white py-1 rounded text-xs">
            🏃 Tactical Retreat
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-950 text-white p-4">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-4">
          <h1 className="text-2xl text-yellow-400 font-bold">三國志 TEXT SIM</h1>
          <p className="text-gray-500 text-sm">ROTK11-Inspired Strategy Game Demo</p>
        </div>

        {/* Navigation */}
        <div className="flex gap-2 mb-4 justify-center flex-wrap">
          {[
            { id: 'map', label: '🗺️ Map', color: 'yellow' },
            { id: 'city', label: '🏰 City', color: 'green' },
            { id: 'officer', label: '👤 Officer', color: 'blue' },
            { id: 'battle', label: '⚔️ Battle', color: 'orange' },
            { id: 'duel', label: '🤺 Duel', color: 'red' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setView(tab.id)}
              className={`px-3 py-1 rounded text-sm transition ${
                view === tab.id 
                  ? `bg-${tab.color}-600 text-white` 
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
          {view === 'map' && renderMap()}
          {view === 'city' && renderCityDetail()}
          {view === 'officer' && renderOfficer()}
          {view === 'battle' && renderBattle()}
          {view === 'duel' && renderDuel()}
        </div>

        {/* Status Bar */}
        <div className="mt-4 bg-gray-800 rounded p-2 flex justify-between text-xs">
          <span className="text-green-400">蜀 SHU │ Cities: 2 │ Officers: 12</span>
          <span className="text-yellow-400">💰 5,400 │ 🍚 23,000 │ ⚔️ 35,000</span>
          <span className="text-gray-400">Spring 194 AD</span>
        </div>

        <div className="mt-4 text-center text-xs text-gray-600">
          <p>This is a demo of the enhanced UI. Click the tabs to explore different views!</p>
          <p>The Duel tab is interactive - try fighting Xiahou Dun!</p>
        </div>
      </div>
    </div>
  );
};

export default SangoTextSimDemo;
