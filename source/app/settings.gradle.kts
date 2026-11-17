// settings.gradle.kts -- This file is part of tiny_container.
//
// Copyright (C) 2026 Caten Hu
//
// Tiny Container is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published
// by the Free Software Foundation, either version 3 of the License,
// or any later version.
//
// Tiny Container is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty
// of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
// See the GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see http://www.gnu.org/licenses/.

/**
 * Locates the local maven repository that holds our patched AVNC AAR
 * (`com.github.tiny-computer:avnc:<version>`).
 *
 * The original workspace keeps it at
 *   <workspace>/refs-reference-assets-deletable/maven-local
 * which is two levels above `source/app`, so a plain absolute path would break for
 * anyone who clones this repo somewhere else. Resolution order:
 *
 *   1. $AVNC_MAVEN_LOCAL                                    explicit override
 *   2. <ancestor>/avnc-maven-local                          portable drop-in location
 *   3. <ancestor>/refs-reference-assets-deletable/maven-local   original workspace
 *
 * Walking ancestors (instead of a fixed relative path) keeps this working whether
 * this file sits at `<workspace>/source/app` or `<workspace>/tiny_container`.
 * When nothing exists we return the portable drop-in path, so the error the user
 * sees is an unresolved dependency plus a path they can recognise and populate.
 */
fun resolveAvncMavenLocal(): String {
    System.getenv("AVNC_MAVEN_LOCAL")?.let { return java.io.File(it).absolutePath }
    val relPaths = listOf(
        "avnc-maven-local",
        "refs-reference-assets-deletable/maven-local",
    )
    var dir: java.io.File? = settingsDir
    while (dir != null) {
        for (rel in relPaths) {
            val candidate = java.io.File(dir, rel)
            if (candidate.isDirectory) return candidate.absolutePath
        }
        dir = dir.parentFile
    }
    return java.io.File(settingsDir.parentFile, "avnc-maven-local").absolutePath
}

pluginManagement {
    repositories {
        google {
            content {
                includeGroupByRegex("com\\.android.*")
                includeGroupByRegex("com\\.google.*")
                includeGroupByRegex("androidx.*")
            }
        }
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        // Local fork: patched AVNC AAR (zoom lock, pointer tuning, cursor size/colour,
        // scroll speed, zoom mis-touch guard). Must come BEFORE jitpack so the local
        // artifact wins the lookup.
        //
        // Location is resolved in this order:
        //   1. $env:AVNC_MAVEN_LOCAL                                  (explicit override)
        //   2. <any ancestor dir>/avnc-maven-local                     (portable checkout)
        //   3. <any ancestor dir>/refs-reference-assets-deletable/maven-local
        //                                                              (original workspace)
        // If none exists, the configured-but-empty path is used and Gradle will simply
        // fail to resolve the artifact, which is the honest error for "you did not
        // build the AVNC fork yet" (see docs/build-and-upstream-sync.md).
        maven {
            url = uri(resolveAvncMavenLocal())
            metadataSources { mavenPom(); artifact() }
        }
        maven { url = uri("https://jitpack.io") }
    }
}

rootProject.name = "Tiny Container"
include(":app")