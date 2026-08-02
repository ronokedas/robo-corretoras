<?php

namespace Tests\Feature;

// use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\ViewErrorBag;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    /**
     * A basic test example.
     */
    public function test_the_application_returns_a_successful_response(): void
    {
        $response = $this->get('/');

        $response->assertRedirect('/admin/licenses');
    }

    public function test_login_urls_support_a_reverse_proxy_subdirectory(): void
    {
        $this->app['url']->forceRootUrl('https://www.4dtech.com.br/robo');
        $this->app['url']->forceScheme('https');
        $html = view('auth.login', ['errors' => new ViewErrorBag()])->render();

        $this->assertStringContainsString('href="https://www.4dtech.com.br/robo/admin.css"', $html);
        $this->assertStringContainsString('action="https://www.4dtech.com.br/robo/login"', $html);
    }
}
