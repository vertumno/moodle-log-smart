/**
 * AIOS Project Configuration
 * Synkra AIOS Framework Configuration for moodle-log-smart
 */

module.exports = {
  project: {
    name: 'moodle-log-smart',
    description: 'Sistema inteligente de análise de logs do Moodle',
    version: '1.0.0',
    type: 'brownfield', // brownfield | greenfield
    stack: 'fullstack', // fullstack | service | ui
    status: 'in-development'
  },

  framework: {
    basePath: '.aios-core',
    development: {
      tasks: 'development/tasks',
      templates: 'development/templates',
      workflows: 'development/workflows',
      agents: 'development/agents',
      checklists: 'development/checklists',
      data: 'development/data',
      utils: 'development/utils'
    },
    logs: {
      path: 'logs',
      level: 'info' // debug | info | warn | error
    }
  },

  team: {
    masterId: 'aios-master',
    agents: [
      'aios-master',
      'dev',
      'qa',
      'architect',
      'pm',
      'po',
      'sm',
      'analyst',
      'data-engineer',
      'ux-design-expert',
      'github-devops'
    ]
  },

  development: {
    mainBranch: 'master',
    packageManager: 'npm',
    runtime: 'node',
    testFramework: 'jest'
  },

  git: {
    conventional_commits: true,
    require_story_reference: true,
    story_prefix: 'Story'
  }
};
