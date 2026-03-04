#!/usr/bin/env python3
"""Check if lesson_controller can be imported and routes are registered"""
import sys

try:
    from app.controllers import lesson_controller
    
    print('✅ lesson_controller imported successfully')
    print()
    print('Routes in lesson_controller.router:')
    print()
    
    for route in lesson_controller.router.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ', '.join(route.methods)
            print(f'  {methods:8} {route.path}')
            
    print()
    
    # Check specifically for quiz route
    quiz_routes = [r for r in lesson_controller.router.routes 
                   if hasattr(r, 'path') and 'quiz' in r.path]
    
    if quiz_routes:
        print('✅ Quiz route FOUND in controller!')
        for r in quiz_routes:
            print(f'   Path: {r.path}')
            print(f'   Methods: {r.methods}')
    else:
        print('❌ Quiz route NOT FOUND in controller!')
        
except Exception as e:
    print(f'❌ Error importing lesson_controller:')
    print(f'   {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
