# version_info.py - Sistema de versiones automático basado en Git
import subprocess
import os
from datetime import datetime

def get_git_version():
    """Obtiene información de versión desde Git"""
    try:
        # Obtener hash del commit actual (corto)
        commit_hash = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'], 
            stderr=subprocess.DEVNULL,
            cwd=os.path.dirname(os.path.abspath(__file__))
        ).decode('utf-8').strip()
        
        # Obtener fecha del último commit
        commit_date = subprocess.check_output(
            ['git', 'log', '-1', '--format=%cd', '--date=short'], 
            stderr=subprocess.DEVNULL,
            cwd=os.path.dirname(os.path.abspath(__file__))
        ).decode('utf-8').strip()
        
        # Verificar si hay cambios sin commit
        try:
            subprocess.check_output(
                ['git', 'diff-index', '--quiet', 'HEAD', '--'], 
                stderr=subprocess.DEVNULL,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            dirty = False
        except subprocess.CalledProcessError:
            dirty = True
        
        # Obtener rama actual
        try:
            branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                stderr=subprocess.DEVNULL,
                cwd=os.path.dirname(os.path.abspath(__file__))
            ).decode('utf-8').strip()
        except:
            branch = "unknown"
        
        # Formatear versión
        version = f"v5.0-{commit_hash}"
        if dirty:
            version += "-dirty"
            
        return {
            'version': version,
            'commit': commit_hash,
            'date': commit_date,
            'branch': branch,
            'dirty': dirty,
            'full_info': f"{version} ({commit_date})"
        }
        
    except Exception as e:
        # Fallback si Git no está disponible
        return {
            'version': 'v5.0-unknown',
            'commit': 'unknown',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'branch': 'unknown',
            'dirty': False,
            'full_info': f"v5.0-unknown ({datetime.now().strftime('%Y-%m-%d')})"
        }

def get_build_info():
    """Obtiene información adicional del build"""
    try:
        # Obtener número total de commits
        commit_count = subprocess.check_output(
            ['git', 'rev-list', '--count', 'HEAD'], 
            stderr=subprocess.DEVNULL,
            cwd=os.path.dirname(os.path.abspath(__file__))
        ).decode('utf-8').strip()
        
        return {
            'build_number': commit_count,
            'build_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except:
        return {
            'build_number': 'unknown',
            'build_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def get_version_string():
    """Retorna string de versión completo para mostrar"""
    git_info = get_git_version()
    build_info = get_build_info()
    
    return f"{git_info['version']} (build #{build_info['build_number']})"

def get_version_badge():
    """Retorna HTML para badge de versión"""
    git_info = get_git_version()
    build_info = get_build_info()
    
    # Color del badge según estado
    if git_info['dirty']:
        badge_color = '#f59e0b'  # Amarillo para cambios sin commit
        status_icon = '🔧'
    elif git_info['branch'] != 'main':
        badge_color = '#3b82f6'  # Azul para otras ramas
        status_icon = '🌿'
    else:
        badge_color = '#22c55e'  # Verde para main limpio
        status_icon = '✅'
    
    return f"""
    <div class="version-badge" style="
        position: fixed;
        bottom: 10px;
        right: 10px;
        background: {badge_color};
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        z-index: 1000;
        font-family: 'Courier New', monospace;
        cursor: pointer;
        transition: all 0.3s ease;
    " title="Commit: {git_info['commit']} | Fecha: {git_info['date']} | Rama: {git_info['branch']} | Build: #{build_info['build_number']}"
    onmouseover="this.style.transform='scale(1.05)'"
    onmouseout="this.style.transform='scale(1)'">
        {status_icon} {git_info['version']}
    </div>
    """
